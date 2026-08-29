import pathlib

from rdflib import OWL, RDF, RDFS, SKOS, XSD as RDF_XSD, Literal, Namespace

from openfoodfacts_taxonomy_parser.parser.logger import ParserConsoleLogger
from openfoodfacts_taxonomy_parser.parser.rdf_parser import OFF, parse_to_rdf

TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test.txt")
TEST_PROPERTY_CONFUSED_LANG_TXT = str(
    pathlib.Path(__file__).parent.parent / "data" / "test_property_confused_lang.txt"
)
TEST_RDF_ENTRIES_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test_rdf_entries.txt")


def test_rdf_parser():
    graph = parse_to_rdf(TEST_TAXONOMY_TXT)

    # Check concept scheme
    assert (OFF.test, RDF.type, SKOS.ConceptScheme) in graph
    assert (OFF.test, SKOS.prefLabel, Literal("Test", "en")) in graph

    # Check class definition
    assert (OFF.Test, RDFS.subClassOf, SKOS.Concept) in graph

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
    assert (test["passion-fruit-yogurts"], SKOS.broader, test.yogurts) in graph

    # Top concepts
    assert (test.meat, SKOS.topConceptOf, OFF.test) in graph
    # Yogurt has a parent of milk which is not in the file, so shows as a top concept
    assert (test.yogurts, SKOS.topConceptOf, OFF.test) in graph
    assert (test['banana-yogurts'], SKOS.topConceptOf, OFF.test) not in graph

    # Properties
    assert (test.meat, OFF.carbonFootprintFrFoodgesValue, Literal("10", "fr")) in graph

    # Check properties that have appeared on instances appear on the class
    assert (OFF.carbonFootprintFrFoodgesValue, RDF.type, RDF.Property) in graph
    assert (OFF.carbonFootprintFrFoodgesValue, RDFS.domain, OFF.Test) in graph
    assert (OFF.carbonFootprintFrFoodgesValue, RDFS.range, RDF_XSD.string) in graph


def test_rdf_description():
    graph = parse_to_rdf(TEST_PROPERTY_CONFUSED_LANG_TXT)

    ns = Namespace("https://openfoodfacts.org/data/taxonomies/test_property_confused_lang#")

    # Check that the description uses the SKOS definition
    assert (
        ns["1-for-the-planet"],
        SKOS.definition,
        Literal(
            "Commit to donating at least 1% of annual sales to environmental organizations.", "en"
        ),
    ) in graph

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
    assert (NS.tomato, OFF.ciqualFoodCode, CIQUAL["20047"]) in graph

    # CIQUAL property is defined in the graph
    assert (OFF.ciqualFoodCode, RDFS.subPropertyOf, SKOS.exactMatch) in graph
    assert (OFF.ciqualFoodCode, RDF.type, OWL.ObjectProperty) in graph
    assert (OFF.ciqualFoodCode, RDFS.domain, OFF.TestRdfEntry) in graph

    assert (NS.tomato, OFF.ciqualFoodName, Literal("Tomato, raw", "en")) in graph
    assert (OFF.ciqualFoodName, RDFS.subPropertyOf, SKOS.altLabel) in graph
    assert (OFF.ciqualFoodName, RDF.type, OWL.AnnotationProperty) in graph

    # Ciqual proxy codes mapped correctly
    assert (NS.pumpkin, OFF.ciqualProxyFoodCode, CIQUAL["20139"]) in graph
    assert (OFF.ciqualProxyFoodCode, RDFS.subPropertyOf, SKOS.closeMatch) in graph
    assert (NS.pumpkin, OFF.ciqualProxyFoodName, Literal("Courge, crue", "fr")) in graph
    assert (OFF.ciqualProxyFoodName, RDFS.subPropertyOf, SKOS.altLabel) in graph

    # Check naming of unknown properties
    assert (NS.pumpkin, OFF.randomProperty, Literal("test", "en")) in graph

    # Vegan status
    assert (NS.tomato, OFF.vegan, OFF.isVegan) in graph
    assert (NS.filling, OFF.vegan, OFF.maybeVegan) in graph

    # Vegan metadata
    assert (OFF.veganStatus, RDF.type, OWL.Class) in graph
    assert (OFF.vegan, RDF.type, OWL.ObjectProperty) in graph
    assert (OFF.isVegan, RDFS.subClassOf, OFF.veganStatus) in graph
    assert (OFF.maybeVegan, RDFS.subClassOf, OFF.veganStatus) in graph
    assert (OFF.notVegan, RDFS.subClassOf, OFF.veganStatus) in graph
    assert (OFF.vegan, RDFS.domain, OFF.TestRdfEntry) in graph
    assert (OFF.vegan, RDFS.range, OFF.veganStatus) in graph

    # Warning about unknown vegan status
    assert any(
        "unknown" in warning and "duplicate-item" in warning for warning in logger.parsing_warnings
    )
    # But still added to the graph
    assert (NS["duplicate-item"], OFF.vegan, Literal("unknown", "en")) in graph

    # Use canonical id of parent when an alias is used in the taxonomy
    assert (NS["apricot-filling"], SKOS.broader, NS.filling) in graph

    # Entries with invalid parents should appear in the top level
    assert (NS["has-invalid-parent"], SKOS.topConceptOf, OFF["test_rdf_entries"]) in graph
    assert any(
        "has-invalid-parent" in error and "invalid-parent" in error
        for error in logger.parsing_errors
    )
