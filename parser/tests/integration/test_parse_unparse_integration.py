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
    query = "MATCH (n:p_test_branch) DETACH DELETE n"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchIds IF EXISTS"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchTagsIds IF EXISTS"
    neo4j.session().run(query)

    query1 = "MATCH (n:p_test_branch1) DETACH DELETE n"
    neo4j.session().run(query1)
    query1 = "DROP INDEX p_test_branch1_SearchIds IF EXISTS"
    neo4j.session().run(query1)
    query1 = "DROP INDEX p_test_branch1_SearchTagsIds IF EXISTS"
    neo4j.session().run(query1)

    query2 = "MATCH (n:p_test_branch2) DETACH DELETE n"
    neo4j.session().run(query2)
    query2 = "DROP INDEX p_test_branch2_SearchIds IF EXISTS"
    neo4j.session().run(query2)
    query2 = "DROP INDEX p_test_branch2_SearchTagsIds IF EXISTS"
    neo4j.session().run(query2)


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

        # make some modifications
        modified = datetime.datetime.now().timestamp()
        # modify entry yogourts
        result = session.run(
            f"""
            MATCH (n:p_test_branch)
            WHERE n.id = "en:yogurts"
            SET n.tags_en = ["en:yogurts", "en:yogurt", "en:yooghurt"], n.modified = {modified}
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
        assert result.values() == [["en:yogurts", "en:banana-yogurts"]]
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
        result = session.run(
            f"""
            MATCH (n:p_test_branch) - [] - (m:p_test_branch)
            WHERE m.id = "en:passion-fruit-yogurts"
            DETACH DELETE m
        """
        )
        assert result.values() == [1]
        # TODO:
        # add new entry with parents
        # add new entry child of this one --> end of file
        # add new entry without parents --> end of file
        session.run(
            f"""
            MATCH (n:p_test_branch)
            WHERE n.id = "en:yogurts"
            SET n.tags_en = ["en:yogurts", "en:yogurt", "en:yooghurt"]
            modified = {modified}
        """
        )

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
