import pathlib

from rdflib import RDF, SKOS, Literal, Namespace

from openfoodfacts_taxonomy_parser.parser.rdf_parser import OFF, parse_to_rdf

TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test.txt")

def test_rdf_parser():
    graph = parse_to_rdf(TEST_TAXONOMY_TXT)
    
    # Check concept scheme
    assert (OFF.test, RDF.type, SKOS.ConceptScheme) in graph
    assert (OFF.test, SKOS.prefLabel, Literal("Test", "en")) in graph

    # Check that all concepts are present in the graph
    test = Namespace("https://openfoodfacts.org/data/taxonomies/test#")
    assert (test.yogurts, RDF.type, SKOS.Concept) in graph
    assert (test.yogurts, SKOS.inScheme, OFF.test) in graph
    
    # Preferred labels
    assert (test.yogurts, SKOS.prefLabel, Literal("yogurts", "en")) in graph
    assert (test.yogurts, SKOS.prefLabel, Literal("yaourts", "fr")) in graph
    
    # Synonyms
    assert (test.yogurts, SKOS.altLabel, Literal("yoghurts", "en")) in graph
    assert (test.yogurts, SKOS.altLabel, Literal("yoghourts", "fr")) in graph
