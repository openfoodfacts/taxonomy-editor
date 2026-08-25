import pathlib

from rdflib import OWL, RDF, RDFS, SKOS, XSD as RDF_XSD, Literal, Namespace

from openfoodfacts_taxonomy_parser.parser.logger import ParserConsoleLogger
from openfoodfacts_taxonomy_parser.parser.rdf_parser import OFF, parse_to_rdf

TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test.txt")
TEST_PROPERTY_CONFUSED_LANG_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test_property_confused_lang.txt")
TEST_RDF_ENTRIES_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test_rdf_entries.txt")

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

def test_rdf_description():
    graph = parse_to_rdf(TEST_PROPERTY_CONFUSED_LANG_TXT)
    
    ns = Namespace("https://openfoodfacts.org/data/taxonomies/test_property_confused_lang#")

    # Check that the description uses the SKOS definition
    assert (ns['1-for-the-planet'], SKOS.definition, Literal("Commit to donating at least 1% of annual sales to environmental organizations.", "en")) in graph
    
    # Captialization of class name
    assert (OFF.TestPropertyConfusedLang, RDFS.subClassOf, SKOS.Concept) in graph


def test_rdf_full():
    logger = ParserConsoleLogger()
    graph = parse_to_rdf(TEST_RDF_ENTRIES_TXT, logger=logger)
    
    NS = Namespace("https://openfoodfacts.org/data/taxonomies/test_rdf_entries#")
    CIQUAL = Namespace("https://ico.iate.inra.fr/meatylab/origin_databases/2/foods/")

    # Captialization of class name
    assert (OFF.TestRdfEntry, RDFS.subClassOf, SKOS.Concept) in graph
    
    # Warning about duplicate item
    assert any("duplicate-item" in warning for warning in logger.parsing_warnings)
    
    # Ciqual codes mapped correctly
    assert (NS.tomato, OFF.ciqualCode, CIQUAL['20047']) in graph
    
    # CIQUAL property is defined in the graph
    assert (OFF.ciqualCode, RDFS.subPropertyOf, SKOS.exactMatch) in graph
    assert (OFF.ciqualCode, RDF.type, OWL.ObjectProperty) in graph
    assert (OFF.ciqualCode, RDFS.domain, OFF.TestRdfEntry) in graph
