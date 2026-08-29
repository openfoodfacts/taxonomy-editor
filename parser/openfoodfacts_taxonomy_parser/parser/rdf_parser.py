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

from rdflib import RDF, RDFS, SKOS, Graph, Literal, Namespace

from .logger import ParserConsoleLogger
from .rdf_properties import PROPERTY_MAP, CIQUAL, OFF, add_default_property
from .taxonomy_parser import TaxonomyParser


inflect_engine = inflect.engine()


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
        for parent in [parent for parent in taxonomy.child_links if parent['id'] == node.id]:
            parent_concept = ns[parent['parent_id'].split(":", 1)[1]]
            graph.add((concept, SKOS.broader, parent_concept))

        if not node.parent_tags:
            graph.add((concept, SKOS.topConceptOf, scheme))

        # Properties
        for property_tag, value in node.properties.items():
            parts = property_tag.rsplit("_", 1)  # Extract the language suffix
            property_name = parts[0][5:]  # Remove the "prop_" prefix
            lang = parts[1]
            property_definition = PROPERTY_MAP.get(property_name)
            if property_definition:
                property_definition.add(logger, graph, OFF[class_name], concept, value, lang)
            else:
                add_default_property(graph, OFF[class_name], concept, property_name, value, lang)

    graph.serialize(destination="debug.ttl")
    return graph


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "tests/data/test"

    # Pass session variable to parser object
    graph = parse_to_rdf(f"{filename}.txt")
    graph.serialize(destination=f"{filename}.ttl")

