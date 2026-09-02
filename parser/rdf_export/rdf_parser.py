"""
Converts OpenFoodFacts taxonomy files to RDF format using the rdflib library.

To use from the command line, run:

python -m rdf_export.rdf_parser <taxonomy_file> <output_dir> <scheme_id>

Do not include the txt extension in the taxonomy file path.

This will generate a corresponding .ttl file in the output directory,
or the current directory if no output_dir is specified.

If the scheme_id is not specified then the file name, without path, will be used.
"""

import re
import sys
from pathlib import Path

import inflect
from rdflib import RDF, RDFS, SKOS, Graph, Literal, Namespace

from rdf_export.rdf_context import RdfContext

from openfoodfacts_taxonomy_parser.parser.logger import ParserConsoleLogger
from .rdf_properties import NAMESPACE_PREFIXES, OFF, PROPERTY_MAP, ROOT, add_default_property
from openfoodfacts_taxonomy_parser.parser.taxonomy_parser import TaxonomyParser

inflect_engine = inflect.engine()


def parse_to_rdf(filename, scheme_id=None, logger=None) -> Graph:
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

    # Create the core namespace prefix
    graph.bind(NAMESPACE_PREFIXES[OFF], OFF)

    # Create a concept scheme for the taxonomy
    scheme_id = scheme_id or Path(filename).stem
    scheme_label = scheme_id.replace("_", " ").title()
    scheme = OFF[scheme_id]
    graph.add((scheme, RDF.type, SKOS.ConceptScheme))
    graph.add((scheme, SKOS.prefLabel, Literal(scheme_label, "en")))

    # Create a class for each taxonomy entry
    class_name = scheme_id.title().replace("_", "")
    class_name = inflect_engine.singular_noun(class_name) or class_name
    class_uri = OFF[class_name]
    graph.add((class_uri, RDFS.subClassOf, SKOS.Concept))

    ns = Namespace(f"{ROOT}/{scheme_id}#")
    graph.bind(scheme_id, ns)

    context = RdfContext(taxonomy, graph, ns, logger, class_uri)

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
        has_parent = False
        for parent in [parent for parent in taxonomy.child_links if parent["id"] == node.id]:
            parent_concept = ns[parent["parent_id"].split(":", 1)[1]]
            graph.add((concept, SKOS.broader, parent_concept))
            has_parent = True

        if not has_parent:
            graph.add((concept, SKOS.topConceptOf, scheme))

        # Properties
        for property_tag, value in node.properties.items():
            parts = property_tag.lower().rsplit("_", 1)  # Extract the language suffix
            property_name = parts[0][5:]  # Remove the "prop_" prefix
            lang = parts[1]
            property_definition = PROPERTY_MAP.get(property_name)
            context.concept = concept
            if property_definition:
                property_definition.add(context, value, lang)
            else:
                add_default_property(context, property_name, value, lang)

    # graph.serialize(destination="debug.ttl")
    return graph


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "tests/data/test"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    scheme_id = sys.argv[3] if len(sys.argv) > 3 else Path(filename).stem

    graph = parse_to_rdf(f"{filename}.txt", scheme_id)
    graph.serialize(destination=f"{output_dir}/{scheme_id}.ttl")
