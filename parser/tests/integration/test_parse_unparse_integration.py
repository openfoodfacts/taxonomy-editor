import datetime
import pathlib

import pytest

from openfoodfacts_taxonomy_parser import parser, patcher, unparser

# taxonomy in text format : test.txt
TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test.txt")
TEST_EXTERNAL_1_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test_external1.txt")
TEST_EXTERNAL_2_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test_external2.txt")


@pytest.fixture(autouse=True)
def test_setup(neo4j):
    # delete all the nodes, relations and search indexes in the database
    for label in ["p_test_branch", "p_test_branch1", "p_test_branch2"]:
        query = f"MATCH (n:{label}) DETACH DELETE n"
        neo4j.session().run(query)
        query = f"MATCH (n:REMOVED_{label}) DETACH DELETE n"
        neo4j.session().run(query)
        query = f"DROP INDEX {label}_SearchIds IF EXISTS"
        neo4j.session().run(query)
        query = f"DROP INDEX {label}_SearchTagsIds IF EXISTS"
        neo4j.session().run(query)


def add_project_node(session, branch_name, taxonomy_name):
    query = f"""CREATE (p:PROJECT)
    SET p.branch_name = "{branch_name}"
    SET p.taxonomy_name = "{taxonomy_name}"
    """
    session.run(query)


def test_round_trip(neo4j):
    """test parsing and dumping back a taxonomy"""
    with neo4j.session() as session:
        test_parser = parser.Parser(session)

        # parse taxonomy
        test_parser(TEST_TAXONOMY_TXT, None, "branch", "test")
        # just quick check it runs ok with total number of nodes
        query = "MATCH (n:p_test_branch) RETURN COUNT(*)"
        result = session.run(query)
        number_of_nodes = result.value()[0]
        assert number_of_nodes == 14

        # dump taxonomy back
        test_dumper = unparser.WriteTaxonomy(session)
        lines = list(test_dumper.iter_lines("branch", "test"))

    original_lines = [line.rstrip("\n") for line in open(TEST_TAXONOMY_TXT)]
    # expected result is close to original file with a few tweaks
    expected_lines = []
    for line in original_lines:
        # first tweak: spaces between stopwords
        if line.startswith("stopwords:fr: aux"):
            line = "stopwords:fr: aux, au, de, le, du, la, a, et, test normalisation"
        # second tweak: renaming parent
        elif line.startswith("< fr:yaourts fruit de la passion"):
            line = "< en:Passion fruit yogurts"
        # third tweak: commenting non existing parents
        elif line.startswith("< en:milk"):
            line = "# < en:milk"
        expected_lines.append(line)

    assert expected_lines == lines


def test_two_branch_round_trip(neo4j):
    """test parsing and dumping the same taxonomy with two different branches"""

    with neo4j.session() as session:
        test_parser = parser.Parser(session)

        # parse taxonomy with branch1
        test_parser(TEST_TAXONOMY_TXT, None, "branch1", "test")
        # parse taxonomy with branch2
        test_parser(TEST_TAXONOMY_TXT, None, "branch2", "test")

        # just quick check it runs ok with total number of nodes
        query = "MATCH (n:p_test_branch1) RETURN COUNT(*)"
        result = session.run(query)
        number_of_nodes = result.value()[0]
        assert number_of_nodes == 14

        query = "MATCH (n:p_test_branch2) RETURN COUNT(*)"
        result = session.run(query)
        number_of_nodes = result.value()[0]
        assert number_of_nodes == 14

        # dump taxonomy back
        test_dumper = unparser.WriteTaxonomy(session)
        lines_branch1 = list(test_dumper.iter_lines("branch1", "test"))
        lines_branch2 = list(test_dumper.iter_lines("branch2", "test"))

    original_lines = [line.rstrip("\n") for line in open(TEST_TAXONOMY_TXT)]
    # expected result is close to original file with a few tweaks
    expected_lines = []
    for line in original_lines:
        # first tweak: spaces between stopwords
        if line.startswith("stopwords:fr: aux"):
            line = "stopwords:fr: aux, au, de, le, du, la, a, et, test normalisation"
        # second tweak: renaming parent
        elif line.startswith("< fr:yaourts fruit de la passion"):
            line = "< en:Passion fruit yogurts"
        # third tweak: commenting non existing parents
        elif line.startswith("< en:milk"):
            line = "# < en:milk"
        expected_lines.append(line)

    assert expected_lines == lines_branch1
    assert expected_lines == lines_branch2


def test_round_trip_with_external_taxonomies(neo4j):
    """test parsing and dumping back a taxonomy that has been extended with external taxonomies"""
    with neo4j.session() as session:
        test_parser = parser.Parser(session)

        # parse taxonomy
        test_parser(
            TEST_TAXONOMY_TXT,
            [TEST_EXTERNAL_1_TXT, TEST_EXTERNAL_2_TXT],
            "branch",
            "test",
        )
        # just quick check it runs ok with total number of nodes
        query = "MATCH (n:p_test_branch) RETURN COUNT(*)"
        result = session.run(query)
        number_of_nodes = result.value()[0]
        assert number_of_nodes == 22

        # dump taxonomy back
        test_dumper = unparser.WriteTaxonomy(session)
        lines = list(test_dumper.iter_lines("branch", "test"))

    original_lines = [line.rstrip("\n") for line in open(TEST_TAXONOMY_TXT)]
    # expected result is close to original file with a few tweaks
    expected_lines = []
    for line in original_lines:
        # first tweak: spaces between stopwords
        if line.startswith("stopwords:fr: aux"):
            line = "stopwords:fr: aux, au, de, le, du, la, a, et, test normalisation"
        # second tweak: renaming parent
        elif line.startswith("< fr:yaourts fruit de la passion"):
            line = "< en:Passion fruit yogurts"
        expected_lines.append(line)

    assert expected_lines == lines


def test_round_trip_patcher(neo4j):
    """test parsing and dumping back a taxonomy"""
    with neo4j.session() as session:
        add_project_node(session, "branch", "test")
        test_parser = parser.Parser(session)

        # parse taxonomy
        test_parser(TEST_TAXONOMY_TXT, None, "branch", "test")
        # just quick check it runs ok with total number of nodes
        query = "MATCH (n:p_test_branch) RETURN COUNT(*)"
        result = session.run(query)
        number_of_nodes = result.value()[0]
        assert number_of_nodes == 14

        # dump taxonomy back
        test_dumper = patcher.PatchTaxonomy(session)
        lines = list(test_dumper.iter_lines("branch", "test"))

    original_lines = [line.rstrip("\n") for line in open(TEST_TAXONOMY_TXT)]

    # no tweak with patcher
    assert original_lines == lines


pytest.mark.skip(reason="not finished yet")


def test_patcher_with_modifications(neo4j):
    """test parsing, modifying and dumping back a taxonomy"""
    with neo4j.session() as session:
        add_project_node(session, "branch", "test")
        test_parser = parser.Parser(session)

        # parse taxonomy
        test_parser(TEST_TAXONOMY_TXT, None, "branch", "test")

        # safety check if we get expected node count
        result = session.run("MATCH (n:p_test_branch) RETURN COUNT(*)")
        number_of_nodes = result.value()[0]
        assert number_of_nodes == 14


        # make some modifications
        modified = datetime.datetime.now().timestamp()
        # modify entry yogourts
        result = session.run(
            f"""
            MATCH (n:p_test_branch)
            WHERE n.id = "en:yogurts"
            SET n.tags_en = ["yogurts", "yogurt", "yooghurt"],
                n.tags_ids_en = ["yogurts", "yogurt", "yooghurt"],
                n.modified = {modified}
            RETURN n.id
        """
        )
        assert result.values() == [["en:yogurts"]]
        # remove a node parent
        result = session.run(
            f"""
            MATCH (n:p_test_branch) - [r:is_child_of] -> (m:p_test_branch)
            WHERE m.id = "en:yogurts" AND n.id = "en:banana-yogurts"
            DELETE r
            RETURN n.id, m.id
        """
        )
        assert result.values() == [["en:banana-yogurts", "en:yogurts"]]
        result = session.run(
            f"""
            MATCH (n:p_test_branch)
            WHERE n.id = "en:banana-yogurts"
            SET n.modified = {modified}
            RETURN n.id
        """
        )
        assert result.values() == [["en:banana-yogurts"]]
        # delete an entry
        # we first attach its children to it's parent and mark it as modified
        # QUIRK: which should also modify the previous/next relation,
        # but we don't because there is no need in for this test
        result = session.run(
            f"""
            MATCH (n:p_test_branch)
            WHERE n.id = "fr:yaourts-fruit-passion-alleges"
            SET n.modified = {modified}
            WITH n
            MATCH (m:p_test_branch)
            WHERE m.id = "en:yogurts"
            CREATE (n) - [:is_child_of] -> (m)
            RETURN n.id, m.id
            """
        )
        assert result.values() == [["fr:yaourts-fruit-passion-alleges", "en:yogurts"]]
        # detach the node and set the node as REMOVED
        result = session.run(
            f"""
            MATCH (n:p_test_branch) - [r] - (m:p_test_branch)
            WHERE m.id = "en:passion-fruit-yogurts"
            DELETE r
            REMOVE m:p_test_branch
            SET m:REMOVED_p_test_branch
            SET m.modified = {modified}
            RETURN m.id
        """
        )
        assert result.values() == [["en:passion-fruit-yogurts"]] * 4
        assert result._metadata['stats'] == {'contains-updates': True, 'relationships-deleted': 4, 'labels-added': 1, 'labels-removed': 1, 'properties-set': 4}
        # TODO:
        # add new entry with parents
        # add new entry child of this one --> end of file
        # add new entry without parents --> end of file

        # just quick check it runs ok with total number of nodes
        result = session.run("MATCH (n:p_test_branch) RETURN COUNT(*)")
        number_of_nodes = result.value()[0]
        assert number_of_nodes == 13
        result = session.run("MATCH (n:REMOVED_p_test_branch) RETURN COUNT(*)")
        number_of_nodes = result.value()[0]
        assert number_of_nodes == 1

        # dump taxonomy back
        test_dumper = patcher.PatchTaxonomy(session)
        lines = list(test_dumper.iter_lines("branch", "test"))

    original_lines = [line.rstrip("\n") for line in open(TEST_TAXONOMY_TXT)]

    # expected result is close to original file with a few tweaks
    expected_lines = []
    for num, (line, next_line) in enumerate(zip(original_lines, original_lines[1:] + [None])):
        # changed parent
        if line.startswith("< fr:yaourts fruit de la passion"):
            line = "< en:yogurts"
        # no more parent
        elif line.startswith("< en:yogurts") and next_line.startswith("en: banana yogurts"):
            continue
        # removed entry
        elif num in range(16,20):
            continue
        # changed synonyms
        elif line.startswith("en: yogurts, yoghurts"):
            line = "en: yogurts, yogurt, yooghurt"
        # commenting non existing parents
        elif line.startswith("< en:milk"):
            line = "# < en:milk"
        expected_lines.append(line)
    assert expected_lines == lines
