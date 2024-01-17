import pathlib

import pytest

from openfoodfacts_taxonomy_parser import normalizer, parser

# taxonomy in text format : test.txt
TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test.txt")


@pytest.mark.parametrize(
    "filename, normalized_name",
    [
        ("test", "test.txt"),
        ("test.txt", "test.txt"),
        ("t", "t.txt"),
    ],
)
def test_normalized_filename(filename: str, normalized_name: str):
    taxonomy_parser = parser.TaxonomyParser()
    assert taxonomy_parser._normalized_filename(filename) == normalized_name


def test_fileiter(neo4j):
    taxonomy_parser = parser.TaxonomyParser()
    file_iterator = taxonomy_parser._file_iter(TEST_TAXONOMY_TXT)
    for counter, (_, line) in enumerate(file_iterator):
        assert line == "" or line[0] == "#" or ":" in line
        if counter == 26:
            assert line == "carbon_footprint_fr_foodges_value:fr:10"
    assert counter == 37


@pytest.mark.parametrize(
    "text, normalized_text, lang",
    [
        ("Numéro #1, n°1 des ¾ des Français*", "numero-1-n-1-des-des-francais", "fr"),
        ("Randôm Languäge wìth àccénts", "random-language-with-accents", "fr"),
        ("Randôm Languäge wìth àccénts", "randôm-languäge-wìth-àccénts", "de"),
    ],
)
def test_normalizing(text: str, normalized_text: str, lang: str):
    assert normalizer.normalizing(text, lang) == normalized_text
