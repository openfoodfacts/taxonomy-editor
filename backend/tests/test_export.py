"""Test export feature

The idea is to see if changes made through the api
are then correctly reflected in the exported file.
We use plain text export to avoid dealing with github
"""

import pytest
from fastapi import UploadFile

from editor import graph_db
from editor.controllers import project_controller
from editor.entries import TaxonomyGraph
from editor.models.node_models import EntryNode, NodeType

from .test_utils import FakeBackgroundTask


@pytest.fixture()
async def taxonomy_test(database_lifespan, anyio_backend):
    """We will import a project to work with

    We cache the project by fully duplicating it so that setup is faster
    """
    with open("tests/data/test.txt", "rb") as test_file:
        async with graph_db.TransactionCtx():
            # clean the test project
            await project_controller.delete_project("p_test_branch")
            taxonomy = TaxonomyGraph("template", "test")
            if not await taxonomy.does_project_exist():
                # if the template project is not there, we create it
                background_tasks = FakeBackgroundTask()
                await taxonomy.import_taxonomy(
                    "test taxonomy",
                    "unknown",
                    background_tasks,
                    UploadFile(file=test_file, filename="test.txt"),
                )
            else:
                background_tasks = None
        # this runs in its own transaction
        if background_tasks:
            await background_tasks.run()
        async with graph_db.TransactionCtx():
            # clone template project as test project
            await project_controller.clone_project("template", "test", "branch")
    return TaxonomyGraph("branch", "test")


@pytest.mark.anyio
async def test_no_modification(taxonomy_test):
    background_tasks = FakeBackgroundTask()
    file_path = taxonomy_test.dump_taxonomy(background_tasks)
    assert open(file_path).read() == open("tests/data/test.txt").read()
    # clean files
    await background_tasks.run()


@pytest.mark.anyio
async def test_remove_parent(taxonomy_test):
    async with graph_db.TransactionCtx():
        # remove "yaourts allégés" for "yaourts au fruit de la passion allégés"
        children = await taxonomy_test.get_children("fr:yaourts-alleges")
        children_ids = [record["child.id"] for record in children]
        children_ids.remove("fr:yaourts-fruit-passion-alleges")
        await taxonomy_test.update_node_children("fr:yaourts-alleges", children_ids)
    background_tasks = FakeBackgroundTask()
    file_path = taxonomy_test.dump_taxonomy(background_tasks)
    result = list(open(file_path))
    # expected output
    expected = list(open("tests/data/test.txt"))
    # remaining parent id is now canonical
    expected[44] = "< en:Passion fruit yogurts\n"
    # remove the old parent line
    del expected[45]
    assert result == expected
    # clean files
    await background_tasks.run()


@pytest.mark.anyio
async def test_add_parent(taxonomy_test):
    async with graph_db.TransactionCtx():
        # add "en: fake-stuff" to "yaourts au fruit de la passion allégés"
        children = await taxonomy_test.get_children("en:fake-stuff")
        children_ids = [record["child.id"] for record in children]
        children_ids.append("fr:yaourts-fruit-passion-alleges")
        await taxonomy_test.update_node_children("en:fake-stuff", children_ids)
    background_tasks = FakeBackgroundTask()
    file_path = taxonomy_test.dump_taxonomy(background_tasks)
    result = list(open(file_path))
    # expected output
    expected = list(open("tests/data/test.txt"))
    # parent ids are now canonical and linted
    expected[44] = "< en:Passion fruit yogurts\n"
    expected[45] = "< fr:yaourts allégés\n"
    # new parent added
    expected.insert(46, "< en:fake-stuff\n")
    assert result == expected
    # clean files
    await background_tasks.run()


@pytest.mark.anyio
async def test_add_synonym(taxonomy_test):
    async with graph_db.TransactionCtx():
        # add synonym to yaourts au fruit de la passion
        (node_data,) = await taxonomy_test.get_nodes(
            NodeType.ENTRY, "fr:yaourts-fruit-passion-alleges"
        )
        node = EntryNode(**dict(node_data["n"]))
        node.tags["tags_fr"].append("yaourts allégé aux grenadilles")
        await taxonomy_test.update_node(NodeType.ENTRY, node)
    background_tasks = FakeBackgroundTask()
    file_path = taxonomy_test.dump_taxonomy(background_tasks)
    result = list(open(file_path))
    # expected output
    expected = list(open("tests/data/test.txt"))
    # parent ids are now canonical and linted
    expected[44] = "< en:Passion fruit yogurts\n"
    expected[45] = "< fr:yaourts allégés\n"
    # added the synonyms
    expected[46] = "fr: yaourts au fruit de la passion allégés, yaourts allégé aux grenadilles\n"
    assert result == expected
    # clean files
    await background_tasks.run()


@pytest.mark.anyio
async def test_remove_synonym(taxonomy_test):
    async with graph_db.TransactionCtx():
        # add synonym to yaourts au fruit de la passion
        (node_data,) = await taxonomy_test.get_nodes(NodeType.ENTRY, "en:yogurts")
        node = EntryNode(**dict(node_data["n"]))
        node.tags["tags_fr"].remove("yoghourts")
        await taxonomy_test.update_node(NodeType.ENTRY, node)
    background_tasks = FakeBackgroundTask()
    file_path = taxonomy_test.dump_taxonomy(background_tasks)
    result = list(open(file_path))
    # expected output
    expected = list(open("tests/data/test.txt"))
    # removed the synonyms
    expected[9] = "fr: yaourts, yogourts\n"
    # also properties were re-ordered (linting)
    expected.insert(11, expected.pop(13))
    assert result == expected
    # clean files
    await background_tasks.run()


@pytest.mark.anyio
async def test_no_comment_repeat(taxonomy_test):
    # we had a bug of repeating comments when modifying an entry
    # test it
    async with graph_db.TransactionCtx():
        # just do a null edit on an entry with comments above it
        (node_data,) = await taxonomy_test.get_nodes(NodeType.ENTRY, "en:soup")
        node = EntryNode(**dict(node_data["n"]))
        await taxonomy_test.update_node(NodeType.ENTRY, node)
    background_tasks = FakeBackgroundTask()
    file_path = taxonomy_test.dump_taxonomy(background_tasks)
    result = list(open(file_path))
    # expected output unchanged
    expected = list(open("tests/data/test.txt"))
    assert result == expected
    # clean files
    await background_tasks.run()


@pytest.mark.anyio
async def test_add_bare_child(taxonomy_test):
    async with graph_db.TransactionCtx():
        # add a children to "en:yogurts", without any other properties
        children = await taxonomy_test.get_children("en:yogurts")
        children_ids = [record["child.id"] for record in children]
        children_ids.append("en:sweet yogurts")
        await taxonomy_test.update_node_children("en:yogurts", children_ids)
    background_tasks = FakeBackgroundTask()
    file_path = taxonomy_test.dump_taxonomy(background_tasks)
    result = list(open(file_path))
    # expected output
    expected = list(open("tests/data/test.txt"))
    # new entry inserted just after yogurts, the parent
    expected[16:16] = [
        "< en:yogurts\n",
        "en: sweet yogurts\n",
        "\n",
    ]
    assert result == expected
    # clean files
    await background_tasks.run()


@pytest.mark.anyio
async def test_add_new_entry_as_child(taxonomy_test):
    async with graph_db.TransactionCtx():
        # add as children to "en:yogurts"
        children = await taxonomy_test.get_children("en:yogurts")
        children_ids = [record["child.id"] for record in children]
        children_ids.append("en:sweet-yogurts")
        await taxonomy_test.update_node_children("en:yogurts", children_ids)
        # update entry sweet yogurts
        node = EntryNode(
            id="en:sweet-yogurts",
            preceding_lines=["# yogurts with sugar"],
            main_language="en",
            tags={
                "tags_en": ["sweet yogurts", "yogurts with sugar"],
                "tags_fr": ["yaourts sucrés"],
            },
            properties={"wikipedia_en": "https://fr.wikipedia.org/wiki/Yaourt"},
        )
        await taxonomy_test.update_node(NodeType.ENTRY, node)
        # add a children to this new entry
        await taxonomy_test.update_node_children("en:sweet-yogurts", ["en:edulcorated-yogurts"])
        node = EntryNode(
            id="en:edulcorated-yogurts",
            preceding_lines=[],
            main_language="en",
            tags={"tags_en": ["edulcorated yogurts"]},
            properties={},
        )
        await taxonomy_test.update_node(NodeType.ENTRY, node)

    background_tasks = FakeBackgroundTask()
    file_path = taxonomy_test.dump_taxonomy(background_tasks)
    result = list(open(file_path))
    # expected output
    expected = list(open("tests/data/test.txt"))
    # new entry inserted just after yogurts, the parent
    expected[16:16] = [
        "# yogurts with sugar\n",
        "< en:yogurts\n",
        "en: sweet yogurts, yogurts with sugar\n",
        "fr: yaourts sucrés\n",
        "\n",
        "< en:sweet yogurts\n",
        "en: edulcorated yogurts\n",
        "\n",
    ]
    assert result == expected
    # clean files
    await background_tasks.run()


@pytest.mark.anyio
async def test_add_new_root_entries(taxonomy_test):
    async with graph_db.TransactionCtx():
        # add an entry potatoes
        await taxonomy_test.create_entry_node("Potatoes", "en")
        node = EntryNode(
            id="en:potatoes",
            preceding_lines=["# The real potatoes"],
            main_language="en",
            tags={"tags_en": ["Potatoes"], "tags_fr": ["patates", "pommes de terres"]},
        )
        await taxonomy_test.update_node(NodeType.ENTRY, node)
        # and a child to it
        await taxonomy_test.update_node_children("en:potatoes", ["en:blue-potatoes"])
        node = EntryNode(
            id="en:blue-potatoes",
            main_language="en",
            tags={"tags_en": ["Blue Potatoes"]},
        )
        await taxonomy_test.update_node(NodeType.ENTRY, node)
        # add another unrelated entry cabbage
        await taxonomy_test.create_entry_node("Cabbage", "en")
        node = EntryNode(
            id="en:cabbage",
            main_language="en",
            tags={"tags_en": ["Cabbage"], "tags_fr": ["Choux"]},
        )
        await taxonomy_test.update_node(NodeType.ENTRY, node)
    background_tasks = FakeBackgroundTask()
    file_path = taxonomy_test.dump_taxonomy(background_tasks)
    result = list(open(file_path))
    # expected output
    expected = list(open("tests/data/test.txt"))
    # second entry added at the end
    expected[-1] += "\n"
    expected.extend(
        [
            "\n",
            "# The real potatoes\n",
            "en: Potatoes\n",
            "fr: patates, pommes de terres\n",
            "\n",
            "en: Cabbage\n",
            "fr: Choux\n",
            "\n",
            "< en:Potatoes\n",
            "en: Blue Potatoes\n",
        ]
    )

    assert result == expected
    # clean files
    await background_tasks.run()


@pytest.mark.anyio
async def test_change_entry_id(taxonomy_test):
    async with graph_db.TransactionCtx():
        # change id of entry yogurts
        (node_data,) = await taxonomy_test.get_nodes(NodeType.ENTRY, "en:yogurts")
        node = EntryNode(**dict(node_data["n"]))
        node.tags["tags_en"] = ["yoghurts", "yogurts"]
        await taxonomy_test.update_node(NodeType.ENTRY, node)
    background_tasks = FakeBackgroundTask()
    file_path = taxonomy_test.dump_taxonomy(background_tasks)
    result = list(open(file_path))
    # expected output
    expected = list(open("tests/data/test.txt"))
    # entry yogurts renamed
    expected[8] = "en: yoghurts, yogurts\n"
    # parent renamed for banana yogurts, etc.
    expected[16] = expected[25] = expected[32] = expected[35] = "< en:yoghurts\n"
    # also properties were re-ordered on rewritten entries (linting)
    expected.insert(11, expected.pop(13))
    expected.insert(20, expected.pop(22))
    expected.insert(39, expected.pop(41))
    assert result == expected
    # clean files
    await background_tasks.run()


@pytest.mark.anyio
async def test_remove_entry(taxonomy_test):
    async with graph_db.TransactionCtx():
        # remove "yaourts allégés"
        await taxonomy_test.delete_node(NodeType.ENTRY, "fr:yaourts-alleges")
        # remove meat
        await taxonomy_test.delete_node(NodeType.ENTRY, "en:meat")
    background_tasks = FakeBackgroundTask()
    file_path = taxonomy_test.dump_taxonomy(background_tasks)
    result = list(open(file_path))
    # expected output
    expected = list(open("tests/data/test.txt"))
    # entry removed
    to_remove = [
        32,
        33,
        34,  # yahourts alleges
        62,
        63,
        64,
        65,  # meat
        66,
        73,  # < en:meat
    ]
    # parent changed to "en:yogurts" for "yahourts alleges"
    expected[45] = expected[51] = "< en:yogurts\n"
    # parent normalized
    expected[44] = "< en:Passion fruit yogurts\n"
    expected[50] = "< en:lemon yogurts\n"
    # properties reordered
    # expected.insert(39, expected.pop(41))
    for i in sorted(to_remove, reverse=True):
        del expected[i]
    assert result == expected
    # clean files
    await background_tasks.run()
