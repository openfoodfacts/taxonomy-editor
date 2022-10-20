import os
import pathlib

from neo4j import GraphDatabase

from openfoodfacts_taxonomy_parser import normalizer, parser

# taxonomy in text format : test.txt
TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test.txt")


def test_normalized_filename(neo4j):
    session = neo4j.session()

    x = parser.Parser(session)
    normalizer = x.normalized_filename
    name = normalizer("test")
    assert name == "test.txt"
    name = normalizer("test.txt")
    assert name == "test.txt"
    name = normalizer("t")
    assert name == "t.txt"
    session.close()


def test_fileiter(neo4j):
    session = neo4j.session()
    x = parser.Parser(session)
    file = x.file_iter(TEST_TAXONOMY_TXT)

    for counter, (_, line) in enumerate(file):
        assert line == "" or line[0] == "#" or ":" in line
        if counter == 26:
            assert line == "carbon_footprint_fr_foodges_value:fr:10"
    assert counter == 37
    session.close()


def test_normalizing():
    text = "Numéro #1, n°1 des ¾ des Français*"
    text = normalizer.normalizing(text, "fr")
    assert text == "numero-1-n-1-des-des-francais"
    text = "Randôm Languäge wìth àccénts"
    normal_text = normalizer.normalizing(text, "fr")
    assert normal_text == "random-language-with-accents"
    normal_text = normalizer.normalizing(text, "de")
    assert normal_text == "randôm-languäge-wìth-àccénts"
