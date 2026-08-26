"""
Converts OpenFoodFacts taxonomy files to RDF format using the rdflib library.

To use from the command line, run:
    python -m openfoodfacts_taxonomy_parser.parser.rdf_parser <taxonomy_file without extension>

This will generate a corresponding .ttl file in the same directory as the input file.
"""

from pathlib import Path
import re
import sys
import inflect

from rdflib import OWL, RDF, RDFS, SKOS, XSD as RDF_XSD, Graph, Literal, Namespace, URIRef

from openfoodfacts_taxonomy_parser.parser.logger import ParserConsoleLogger

from .taxonomy_parser import TaxonomyParser

OFF = Namespace("https://openfoodfacts.org/data/taxonomies/core#")
CIQUAL = Namespace("https://ico.iate.inra.fr/meatylab/origin_databases/2/foods/")

inflect_engine = inflect.engine()


def toLowerCamelCase(snake_str):
    first, *others = snake_str.split("_")
    return "".join([first.lower(), *map(str.title, others)])


def parse_to_rdf(filename, logger=None) -> Graph:
    """
    Parse a taxonomy file to RDF format.

    Args:
        filename (str): The path to the taxonomy file.

    Returns:
        rdflib.Graph: The RDF graph containing the parsed taxonomy.
    """
    logger = logger or ParserConsoleLogger()
    taxonomy_parser = TaxonomyParser()
    taxonomy = taxonomy_parser.parse_file(filename, logger=logger)
    graph = Graph()

    # Create the core and commonly used namespace prefixes
    graph.bind("off", OFF)
    graph.bind("ciqual", CIQUAL)

    # Create a concept scheme for the taxonomy
    scheme_id = Path(filename).stem
    scheme_label = scheme_id.replace("_", " ").title()
    scheme = OFF[scheme_id]
    graph.add((scheme, RDF.type, SKOS.ConceptScheme))
    graph.add((scheme, SKOS.prefLabel, Literal(scheme_label, "en")))

    # Create a class for each taxonomy entry
    class_name = scheme_id.title().replace("_", "")
    class_name = inflect_engine.singular_noun(class_name) or class_name
    graph.add((OFF[class_name], RDFS.subClassOf, SKOS.Concept))

    ns = Namespace(f"https://openfoodfacts.org/data/taxonomies/{scheme_id}#")
    graph.bind(scheme_id, ns)

    for node in taxonomy.entry_nodes:
        # As per decision document the language part is not used in the id
        concept = ns[node.id.split(":", 1)[1]]
        if (concept, RDF.type, OFF[class_name]) not in graph:
            graph.add((concept, RDF.type, OFF[class_name]))
            graph.add((concept, SKOS.inScheme, scheme))
        else:
            logger.warning(f"Duplicate canonical identifier: {node.id}")

        # Add labels
        for tag, values in node.tags.items():
            if match := re.search("tags_([^_]*)$", tag):
                lang = match.group(1)
                graph.add((concept, SKOS.prefLabel, Literal(values[0], lang)))

                for synonym in values[1:]:
                    graph.add((concept, SKOS.altLabel, Literal(synonym, lang)))

        # Parents and top concepts
        for parent in node.parent_tags:
            parent_concept = ns[parent[0].split(":", 1)[1]]
            graph.add((concept, SKOS.broader, parent_concept))

        if not node.parent_tags:
            graph.add((concept, SKOS.topConceptOf, scheme))

        # Properties
        for property_tag, value in node.properties.items():
            parts = property_tag.rsplit("_", 1)  # Extract the language suffix
            property_name = parts[0][5:]  # Remove the "prop_" prefix
            property_definition = properties.get(property_name)
            if property_definition:
                property_definition.add(logger, graph, OFF[class_name], concept, value, parts[1])
            else:
                # Unknown property name
                # Convert property names to lowerCamelCase for RDF representation as this follows industry norms
                property_name = toLowerCamelCase(parts[0][5:])
                property = OFF[property_name]
                graph.add((concept, property, Literal(value, parts[1])))

                # Add the property to the class definition if it hasn't been added yet
                if (property, RDF.type, RDF.Property) not in graph:
                    graph.add((property, RDF.type, RDF.Property))
                    graph.add((property, RDFS.domain, OFF[class_name]))
                    graph.add((property, RDFS.range, RDF_XSD.string))

    graph.serialize(destination="debug.ttl")
    return graph


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "tests/data/test"

    # Pass session variable to parser object
    graph = parse_to_rdf(f"{filename}.txt")
    graph.serialize(destination=f"{filename}.ttl")


class PropertyDefinition:
    property: URIRef
    converter: callable
    type: URIRef
    properties: list[tuple[URIRef, URIRef]]
    additional_triples: list[tuple[URIRef, URIRef, URIRef]]

    def __init__(
        self,
        property: URIRef,
        converter: callable = None,
        type: URIRef = None,
        properties: list[tuple[URIRef, URIRef]] = None,
        additional_triples: list[tuple[URIRef, URIRef, URIRef]] = None,
    ):
        self.property = property
        self.converter = converter
        self.type = type
        self.properties = properties or []
        self.additional_triples = additional_triples or []

    def add(self, logger, graph: Graph, class_uri: URIRef, concept: URIRef, value, lang: str):
        graph_value = (
            self.converter(value)
            if self.converter
            else Literal(value, lang)
        )
        if graph_value is None:
            logger.warning(f"Unknown value on {concept.fragment} for property {self.property.fragment}: {value}")
            # Add the raw value to the graph anyway
            graph.add((concept, self.property, Literal(value, lang)))
            return
        if (self.property, None, None) not in graph:
            if self.type:
                graph.add((self.property, RDF.type, self.type))
                # Always add a domain
                graph.add((self.property, RDFS.domain, class_uri))
            if self.properties:
                for prop, obj in self.properties:
                    graph.add((self.property, prop, obj))
            if self.additional_triples:
                for triple in self.additional_triples:
                    graph.add(triple)
        graph.add((concept, self.property, graph_value))


properties = {
    "description": PropertyDefinition(SKOS.definition),
    "ciqual_food_code": PropertyDefinition(
        OFF.ciqualFoodCode,
        lambda x: CIQUAL[x],
        OWL.ObjectProperty,
        [(RDFS.subPropertyOf, SKOS.exactMatch)],
    ),
    "ciqual_proxy_food_code": PropertyDefinition(
        OFF.ciqualProxyFoodCode,
        lambda x: CIQUAL[x],
        OWL.ObjectProperty,
        [(RDFS.subPropertyOf, SKOS.closeMatch)],
    ),
    "ciqual_food_name": PropertyDefinition(
        OFF.ciqualFoodName,
        None,
        OWL.AnnotationProperty,
        [(RDFS.subPropertyOf, SKOS.altLabel)],
    ),
    "ciqual_proxy_food_name": PropertyDefinition(
        OFF.ciqualProxyFoodName,
        None,
        OWL.AnnotationProperty,
        [(RDFS.subPropertyOf, SKOS.altLabel)],
    ),
    "vegan": PropertyDefinition(
        OFF.vegan,
        lambda value: {"yes": OFF.isVegan, "no": OFF.notVegan, "maybe": OFF.maybeVegan}.get(
            value.lower()
        ),
        OWL.ObjectProperty,
        [(RDFS.range, OFF.veganStatus)],
        [
            (OFF.veganStatus, RDF.type, OWL.Class),
            (OFF.isVegan, RDF.type, OWL.Class),
            (OFF.isVegan, RDFS.subClassOf, OFF.veganStatus),
            (OFF.notVegan, RDF.type, OWL.Class),
            (OFF.notVegan, RDFS.subClassOf, OFF.veganStatus),
            (OFF.maybeVegan, RDF.type, OWL.Class),
            (OFF.maybeVegan, RDFS.subClassOf, OFF.veganStatus),
        ],
    ),
}
