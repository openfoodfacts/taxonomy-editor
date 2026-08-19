import pathlib

from rdflib import RDF, RDFS, SKOS, XSD as RDF_XSD, Literal, Namespace

from openfoodfacts_taxonomy_parser.parser.rdf_parser import OFF, parse_to_rdf

TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test.txt")

def test_rdf_parser():
    graph = parse_to_rdf(TEST_TAXONOMY_TXT)
    
    # Check concept scheme
    assert (OFF.test, RDF.type, SKOS.ConceptScheme) in graph
    assert (OFF.test, SKOS.prefLabel, Literal("Test", "en")) in graph
    
    # Check class definition
    assert (OFF.Test, RDFS.subClassOf, SKOS.Concept) in graph
    
    # Check properties that have appeared on instances appear on the class
    assert (OFF.vegan, RDF.type, RDF.Property) in graph
    assert (OFF.vegan, RDFS.domain, OFF.Test) in graph
    assert (OFF.vegan, RDFS.range, RDF_XSD.string) in graph

    # Check that all concepts are present in the graph
    test = Namespace("https://openfoodfacts.org/data/taxonomies/test#")
    assert (test.yogurts, RDF.type, OFF.Test) in graph
    assert (test.yogurts, SKOS.inScheme, OFF.test) in graph
    
    # Preferred labels
    assert (test.yogurts, SKOS.prefLabel, Literal("yogurts", "en")) in graph
    assert (test.yogurts, SKOS.prefLabel, Literal("yaourts", "fr")) in graph
    
    # Synonyms
    assert (test.yogurts, SKOS.altLabel, Literal("yoghurts", "en")) in graph
    assert (test.yogurts, SKOS.altLabel, Literal("yoghourts", "fr")) in graph

    # Parents
    assert (test['passion-fruit-yogurts'], SKOS.broader, test.yogurts) in graph
    
    # Top concepts
    assert (test.meat, SKOS.topConceptOf, OFF.test) in graph
    assert (test.yogurts, SKOS.topConceptOf, OFF.test) not in graph
    
    # Properties
    assert (test.meat, OFF.carbon_footprint_fr_foodges_value, Literal("10", "fr")) in graph
