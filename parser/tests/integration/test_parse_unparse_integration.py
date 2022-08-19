import pathlib

import pytest

from openfoodfacts_taxonomy_parser import parser, unparser

# taxonomy in text format : test.txt
TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test.txt")


@pytest.fixture(autouse=True)
def test_setup():
    # delete all the nodes and relations in the database
    query = "MATCH (n) DETACH DELETE n"
    parser.Parser().session.run(query)


def test_round_trip():
    """test parsing and dumping back a taxonomy"""
    test_parser = parser.Parser()
    session = test_parser.session

    # parse taxonomy
    test_parser(TEST_TAXONOMY_TXT)
    # just quick check it runs ok with total number of nodes
    query = "MATCH (n) RETURN COUNT(*)"
    result = session.run(query)
    number_of_nodes = result.value()[0]
    assert number_of_nodes == 13
    session.close()

    # dump taxonomy back
    test_dumper = unparser.WriteTaxonomy()
    lines = list(test_dumper.iter_lines())

    original_lines = [l.rstrip("\n") for l in open(TEST_TAXONOMY_TXT)]  # remove new lines
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
