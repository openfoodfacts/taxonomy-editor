import pathlib

import pytest

from openfoodfacts_taxonomy_parser import parser, unparser

# taxonomy in text format : test.txt
TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test.txt")


@pytest.fixture(autouse=True)
def test_setup(neo4j):
    # delete all the nodes, relations and search indexes in the database
    query = "MATCH (n:p_test_branch) DETACH DELETE n"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchIds IF EXISTS"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchTags IF EXISTS"
    neo4j.session().run(query)

    query1 = "MATCH (n:p_test_branch1) DETACH DELETE n"
    neo4j.session().run(query1)
    query1 = "DROP INDEX p_test_branch1_SearchIds IF EXISTS"
    neo4j.session().run(query1)
    query1 = "DROP INDEX p_test_branch1_SearchTags IF EXISTS"
    neo4j.session().run(query1)

    query2 = "MATCH (n:p_test_branch2) DETACH DELETE n"
    neo4j.session().run(query2)
    query2 = "DROP INDEX p_test_branch2_SearchIds IF EXISTS"
    neo4j.session().run(query2)
    query2 = "DROP INDEX p_test_branch2_SearchTags IF EXISTS"
    neo4j.session().run(query2)


def test_round_trip(neo4j):
    """test parsing and dumping back a taxonomy"""
    with neo4j.session() as session:
        test_parser = parser.Parser(session)

        # parse taxonomy
        test_parser(TEST_TAXONOMY_TXT, "branch", "test")
        # just quick check it runs ok with total number of nodes
        query = "MATCH (n:p_test_branch) RETURN COUNT(*)"
        result = session.run(query)
        number_of_nodes = result.value()[0]
        assert number_of_nodes == 14

        # dump taxonomy back
        test_dumper = unparser.WriteTaxonomy(session)
        lines = list(test_dumper.iter_lines("p_test_branch"))

    possible_lines = get_possible_lines_for_test_taxonomy()

    assert lines in possible_lines


def test_two_branch_round_trip(neo4j):
    """test parsing and dumping the same taxonomy with two different branches"""

    with neo4j.session() as session:
        test_parser = parser.Parser(session)

        # parse taxonomy with branch1
        test_parser(TEST_TAXONOMY_TXT, "branch1", "test")
        # parse taxonomy with branch2
        test_parser(TEST_TAXONOMY_TXT, "branch2", "test")

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
        lines_branch1 = list(test_dumper.iter_lines("p_test_branch1"))
        lines_branch2 = list(test_dumper.iter_lines("p_test_branch2"))

    possible_lines = get_possible_lines_for_test_taxonomy()

    assert lines_branch1 in possible_lines
    assert lines_branch2 in possible_lines


def get_possible_lines_for_test_taxonomy():
    original_lines = [line.rstrip("\n") for line in open(TEST_TAXONOMY_TXT)]

    # expected result is close to original file with a few tweaks
    expected_lines_1 = []
    expected_lines_2 = []

    for line in original_lines:
        # first tweak: spaces between stopwords
        if line.startswith("stopwords:fr: aux"):
            line = "stopwords:fr:aux, au, de, le, du, la, a, et"
        # second tweak: renaming parent
        elif line.startswith("<fr:yaourts fruit de la passion"):
            line = "<en:Passion fruit yogurts"
        line_1, line_2 = line, line
        # parent order is undeterministic
        if line.startswith("<en:fake-stuff"):
            line_2 = "<en:fake-meat"
        elif line.startswith("<en:fake-meat"):
            line_2 = "<en:fake-stuff"

        expected_lines_1.append(line_1)
        expected_lines_2.append(line_2)

    return [expected_lines_1, expected_lines_2]
