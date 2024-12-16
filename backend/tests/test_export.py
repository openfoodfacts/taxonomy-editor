"""Test export feature

The idea is to see if changes made through the api are then correctly reflected in the exported file.
We use plain text export to avoid dealing with github
"""

import pytest

from fastapi import UploadFile

from editor.controllers import project_controller
from editor.models.node_models import NodeType, EntryNode
from editor.entries import TaxonomyGraph
from editor import graph_db

from .utils import FakeBackgroundTask


@pytest.fixture()
async def taxonomy_test(database_lifespan):
    """We will import a project to work with

    We cache the project by fully duplicating it so that setup is faster
    """
    from .utils import clean_neo4j_db
    # TEMPORARY use this to clean template in the db
    # await clean_neo4j_db(database_lifespan)
    with open("tests/data/test.txt", "rb") as test_file:
        async with graph_db.TransactionCtx() as session:
            # clean the test project
            await project_controller.delete_project("p_test_branch")
            taxonomy = TaxonomyGraph("template", "test")
            if not await taxonomy.does_project_exist():
                # if the template project is not there, we create it
                background_tasks = FakeBackgroundTask()
                await taxonomy.import_taxonomy("test taxonomy", "unknown", background_tasks, UploadFile(file=test_file, filename="test.txt"))
            else:
                background_tasks = None
        # this runs in its own transaction
        if background_tasks:
            await background_tasks.run()
        async with graph_db.TransactionCtx() as session:
            # clone template project as test project
            await project_controller.clone_project("template", "test", "branch")
    return TaxonomyGraph("branch", "test")


@pytest.mark.anyio
async def test_no_modification(taxonomy_test):
    background_tasks = FakeBackgroundTask()
    file_path = taxonomy_test.dump_taxonomy(background_tasks)
    assert open(file_path).read() == open("tests/data/test.txt").read()
    # clean files
    background_tasks.run()

@pytest.mark.anyio
async def test_remove_parent(taxonomy_test):
    async with graph_db.TransactionCtx() as session:
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
    background_tasks.run()


@pytest.mark.anyio
async def test_add_parent(taxonomy_test):
    async with graph_db.TransactionCtx() as session:
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
    background_tasks.run()


@pytest.mark.anyio
async def test_add_synonym(taxonomy_test):
    async with graph_db.TransactionCtx() as session:
        # add synonym to yaourts au fruit de la passion
        node_data, = await taxonomy_test.get_nodes(NodeType.ENTRY, "fr:yaourts-fruit-passion-alleges")
        node = EntryNode(**dict(node_data['n']))
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
    background_tasks.run()


@pytest.mark.anyio
async def test_remove_synonym(taxonomy_test):
    async with graph_db.TransactionCtx() as session:
        # add synonym to yaourts au fruit de la passion
        node_data, = await taxonomy_test.get_nodes(NodeType.ENTRY, "en:yogurts")
        node = EntryNode(**dict(node_data['n']))
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
    background_tasks.run()


@pytest.mark.anyio
async def test_no_comment_repeat(taxonomy_test):
    # we had a bug of repeating comments when modifying an entry
    # test it
    async with graph_db.TransactionCtx() as session:
        # just do a null edit on an entry with comments above it
        node_data, = await taxonomy_test.get_nodes(NodeType.ENTRY, "en:soup")
        node = EntryNode(**dict(node_data['n']))
        await taxonomy_test.update_node(NodeType.ENTRY, node)
    background_tasks = FakeBackgroundTask()
    file_path = taxonomy_test.dump_taxonomy(background_tasks)
    result = list(open(file_path))
    # expected output unchanged
    expected = list(open("tests/data/test.txt"))
    assert result == expected
    # clean files
    background_tasks.run()


@pytest.mark.anyio
async def test_add_new_entry_as_child(taxonomy_test):
    async with graph_db.TransactionCtx() as session:
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
            tags={"tags_en": ["sweet yogurts", "yogurts with sugar"], "tags_fr": ["yaourts sucrés"]},
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
    expected[16:16] =[
        '# yogurts with sugar\n',
        '< en:yogurts\n',
        'en: sweet yogurts, yogurts with sugar\n',
        'fr: yaourts sucrés\n',
        '\n'
    ]
    # second entry added at the end
    expected[-1] += "\n"
    expected.extend([
        '\n', '< en:sweet yogurts\n', 'en: edulcorated yogurts\n'
    ])
    assert result == expected
    # clean files
    background_tasks.run()


@pytest.mark.anyio
async def test_add_new_root_entries(taxonomy_test):
    async with graph_db.TransactionCtx() as session:
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
    expected.extend([
        '\n',
        '< en:Potatoes\n', 'en: Blue Potatoes\n', '\n',
        '# The real potatoes\n', 'en: Potatoes\n', 'fr: patates, pommes de terres\n', '\n',
        'en: Cabbage\n', 'fr: Choux\n'
    ])

    assert result == expected
    # clean files
    background_tasks.run()

@pytest.mark.anyio
async def test_change_entry_id(taxonomy_test):
    # yet to be implemented
    assert False