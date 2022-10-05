import pathlib

from openfoodfacts_taxonomy_parser import parser

# taxonomy in text format : test.txt
TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test.txt")


def test_normalized_filename():
    x = parser.Parser()
    normalizer = x.normalized_filename
    name = normalizer("test")
    assert name == "test.txt"
    name = normalizer("test.txt")
    assert name == "test.txt"
    name = normalizer("t")
    assert name == "t.txt"


def test_fileiter():
    x = parser.Parser()
    file = x.file_iter(TEST_TAXONOMY_TXT)
    for counter, (_, line) in enumerate(file):
        assert line == "" or line[0] == "#" or ":" in line
        if counter == 26:
            assert line == "vegan:en:no"
    assert counter == 37


def test_normalizing():
    x = parser.Parser()
    text = "Numéro #1, n°1 des ¾ des Français*"
    text = x.normalizing(text, "fr")
    assert text == "numero-1-n-1-des-des-francais"
    text = "Randôm Languäge wìth àccénts"
    normal_text = x.normalizing(text, "fr")
    assert normal_text == "random-language-with-accents"
    normal_text = x.normalizing(text, "de")
    assert normal_text == "randôm-languäge-wìth-àccénts"
