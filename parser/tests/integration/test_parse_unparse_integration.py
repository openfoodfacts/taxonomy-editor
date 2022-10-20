import os
import pathlib

import pytest
from neo4j import GraphDatabase

from openfoodfacts_taxonomy_parser import parser, unparser

# taxonomy in text format : test.txt
TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test.txt")


@pytest.fixture(autouse=True)
def test_setup(neo4j):
    # delete all the nodes, relations and search indexes in the database
    query = "MATCH (n:p_test_branch:t_test:b_branch) DETACH DELETE n"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchIds IF EXISTS"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchTags IF EXISTS"
    neo4j.session().run(query)

    query1 = "MATCH (n:p_test_branch1:t_test:b_branch1) DETACH DELETE n"
    neo4j.session().run(query1)
    query1 = "DROP INDEX p_test_branch1_SearchIds IF EXISTS"
    neo4j.session().run(query1)
    query1 = "DROP INDEX p_test_branch1_SearchTags IF EXISTS"
    neo4j.session().run(query1)

    query2 = "MATCH (n:p_test_branch2:t_test:b_branch2) DETACH DELETE n"
    neo4j.session().run(query2)
    query2 = "DROP INDEX p_test_branch2_SearchIds IF EXISTS"
    neo4j.session().run(query2)
    query2 = "DROP INDEX p_test_branch2_SearchTags IF EXISTS"
    neo4j.session().run(query2)


def test_round_trip(neo4j):
    """test parsing and dumping back a taxonomy"""
    session = neo4j.session()
    test_parser = parser.Parser(session)

    # parse taxonomy
    test_parser(TEST_TAXONOMY_TXT, "branch", "test")
    # just quick check it runs ok with total number of nodes
    query = "MATCH (n:p_test_branch:t_test:b_branch) RETURN COUNT(*)"
    result = session.run(query)
    number_of_nodes = result.value()[0]
    assert number_of_nodes == 13

    # dump taxonomy back
    test_dumper = unparser.WriteTaxonomy(session)
    lines = list(test_dumper.iter_lines("p_test_branch:t_test:b_branch"))

    session.close()

    original_lines = [line.rstrip("\n") for line in open(TEST_TAXONOMY_TXT)]
    # expected result is close to original file with a few tweaks
    expected_lines = []
    for line in original_lines:
        # first tweak: spaces between stopwords
        if line.startswith("stopwords:fr: aux"):
            line = "stopwords:fr:aux, au, de, le, du, la, a, et"
        # second tweak: renaming parent
        elif line.startswith("<fr:yaourts fruit de la passion"):
            line = "<en:Passion fruit yogurts"
        # last tweak: parent order
        elif line.startswith("<en:fake-stuff"):
            line = "<en:fake-meat"
        elif line.startswith("<en:fake-meat"):
            line = "<en:fake-stuff"
        expected_lines.append(line)

    assert expected_lines == lines


def test_two_branch_round_trip(neo4j):
    """test parsing and dumping the same taxonomy with two different branches"""

    session = neo4j.session()

    test_parser = parser.Parser(session)

    # parse taxonomy with branch1
    test_parser(TEST_TAXONOMY_TXT, "branch1", "test")
    # parse taxonomy with branch2
    test_parser(TEST_TAXONOMY_TXT, "branch2", "test")

    # just quick check it runs ok with total number of nodes
    query = "MATCH (n:p_test_branch1:t_test:b_branch1) RETURN COUNT(*)"
    result = session.run(query)
    number_of_nodes = result.value()[0]
    assert number_of_nodes == 13

    query = "MATCH (n:p_test_branch2:t_test:b_branch2) RETURN COUNT(*)"
    result = session.run(query)
    number_of_nodes = result.value()[0]
    assert number_of_nodes == 13

    # dump taxonomy back
    test_dumper = unparser.WriteTaxonomy(session)
    lines_branch1 = list(test_dumper.iter_lines("p_test_branch1:t_test:b_branch1"))
    lines_branch2 = list(test_dumper.iter_lines("p_test_branch2:t_test:b_branch2"))

    session.close()

    original_lines = [line.rstrip("\n") for line in open(TEST_TAXONOMY_TXT)]
    # expected result is close to original file with a few tweaks
    expected_lines = []
    for line in original_lines:
        # first tweak: spaces between stopwords
        if line.startswith("stopwords:fr: aux"):
            line = "stopwords:fr:aux, au, de, le, du, la, a, et"
        # second tweak: renaming parent
        elif line.startswith("<fr:yaourts fruit de la passion"):
            line = "<en:Passion fruit yogurts"
        # last tweak: parent order
        elif line.startswith("<en:fake-stuff"):
            line = "<en:fake-meat"
        elif line.startswith("<en:fake-meat"):
            line = "<en:fake-stuff"
        expected_lines.append(line)

    assert expected_lines == lines_branch1
    assert expected_lines == lines_branch2
