"""
Converts OpenFoodFacts taxonomy files to RDF format using the rdflib library.

To use from the command line, run:

python -m rdf_export.rdf_parser <taxonomy_file> <output_dir> <scheme_id>

Do not include the txt extension in the taxonomy file path.

This will generate a corresponding .ttl file in the output directory,
or the current directory if no output_dir is specified.

If the scheme_id is not specified then the file name, without path, will be used.
"""

import argparse
import re
from pathlib import Path

import inflect
from rdflib import RDF, RDFS, SKOS, Graph, Literal

from openfoodfacts_taxonomy_parser.parser.logger import ParserConsoleLogger
from openfoodfacts_taxonomy_parser.parser.taxonomy_parser import TaxonomyParser
from rdf_export.rdf_config import OFF, addTaxonomyNamespace, bindNamespace
from rdf_export.rdf_context import RdfContext

from .rdf_properties import PROPERTY_MAP, add_default_property

inflect_engine = inflect.engine()


def parse_to_rdf(filename, external_filenames = None,scheme_id=None, logger=None) -> Graph:
    """
    Parse a taxonomy file to RDF format.

    Args:
        filename (str): The path to the taxonomy file.
        external_filenames (list, optional): List of external filenames to include in the parsing.
        scheme_id (str, optional): The identifier for the concept scheme and class name.
            Defaults to the file name without extension.
        logger (ParserConsoleLogger, optional): Logger for logging messages.
            Defaults to a new instance of ParserConsoleLogger.

    Returns:
        rdflib.Graph: The RDF graph containing the parsed taxonomy.
    """
    logger = logger or ParserConsoleLogger()
    taxonomy_parser = TaxonomyParser()
    taxonomy = taxonomy_parser.parse_file(filename, external_filenames=external_filenames, logger=logger)
    graph = Graph()

    # Bind the core namespace prefix
    bindNamespace(graph, OFF)

    # Create a concept scheme for the taxonomy
    root_taxonomy = Path(filename).stem
    scheme_id = scheme_id or root_taxonomy
    scheme_label = scheme_id.replace("_", " ").title()
    scheme = OFF[scheme_id]
    graph.add((scheme, RDF.type, SKOS.ConceptScheme))
    graph.add((scheme, SKOS.prefLabel, Literal(scheme_label, "en")))

    # Create a class for each taxonomy entry
    class_name = scheme_id.title().replace("_", "")
    class_name = inflect_engine.singular_noun(class_name) or class_name
    class_uri = OFF[class_name]
    graph.add((class_uri, RDFS.subClassOf, SKOS.Concept))

    ns = addTaxonomyNamespace(scheme_id)
    bindNamespace(graph, ns)

    context = RdfContext(taxonomy, graph, ns, logger)

    for node in taxonomy.entry_nodes:
        my_class = class_uri
        my_scheme = scheme
        my_ns = ns
        my_taxonomy = Path(node.original_taxonomy).stem
        if my_taxonomy != root_taxonomy:
            my_class_name = my_taxonomy.title().replace("_", "")
            my_class_name = inflect_engine.singular_noun(my_class_name) or my_class_name
            my_class = OFF[my_class_name]
            my_scheme = OFF[my_taxonomy]
            my_ns = addTaxonomyNamespace(my_taxonomy)
            if (my_scheme, RDF.type, SKOS.ConceptScheme) not in graph:
                bindNamespace(graph, my_ns)
                graph.add((my_scheme, RDF.type, SKOS.ConceptScheme))
                graph.add((my_scheme, SKOS.prefLabel, Literal(my_taxonomy.replace("_", " ").title(), "en")))
                graph.add((my_class, RDFS.subClassOf, SKOS.Concept))

        # As per decision document the language part is not used in the id
        concept = my_ns[node.id.split(":", 1)[1]]
        if (concept, RDF.type, my_class) not in graph:
            graph.add((concept, RDF.type, my_class))
            graph.add((concept, SKOS.inScheme, scheme))
            # External entries are part of both concept schemes
            if my_scheme != scheme:
                graph.add((concept, SKOS.inScheme, my_scheme))
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
        for parent_id, _ in node.parent_tags:
            parent_id_parts = parent_id.split(":", 1)
            parent_id_tag = parent_id_parts[1]
            parent_id_lang = parent_id_parts[0]
            parent_nodes = [parent_node for parent_node in taxonomy.entry_nodes if parent_node.id == parent_id]
            if not parent_nodes:
                # Try finding by alias
                tag_key = f"tags_ids_{parent_id_lang}"
                parent_nodes = [parent_node for parent_node in taxonomy.entry_nodes if parent_id_tag in parent_node.tags.get(tag_key, [])]
                
            parent_ns = ns
            # If we find the parent node and it is from a different taxonomy, we need to use the namespace of that taxonomy
            if parent_nodes:
                # Only set has_parent to True if we find a parent node in one of the taxonomies
                # otherwise it will remain False and the concept will be added as a top concept
                # which highlights the anomaly
                has_parent = True
                parent_node = parent_nodes[0]
                parent_taxonomy = Path(parent_node.original_taxonomy).stem
                parent_id_tag = parent_node.id.split(":", 1)[1]
                if parent_taxonomy != root_taxonomy:
                    parent_ns = addTaxonomyNamespace(parent_taxonomy)
            parent_concept = parent_ns[parent_id_tag]
            graph.add((concept, SKOS.broader, parent_concept))

        if not has_parent:
            # Add top concepts for all schemes
            graph.add((concept, SKOS.topConceptOf, scheme))
            if my_scheme != scheme:
                graph.add((concept, SKOS.topConceptOf, my_scheme))

        # Properties
        for property_tag, value in node.properties.items():
            parts = property_tag.lower().rsplit("_", 1)  # Extract the language suffix
            property_name = parts[0][5:]  # Remove the "prop_" prefix
            lang = parts[1]
            property_definition = PROPERTY_MAP.get(property_name)
            context.concept = concept
            context.class_uri = my_class
            if property_definition:
                property_definition.add(context, value, lang)
            else:
                add_default_property(context, property_name, value, lang)

    graph.serialize(destination="debug.ttl")
    return graph


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a taxonomy into an RDF Turtle file")
    parser.add_argument(
        "source_dir",
        help="Directory of the taxonomy files",
        default="tests/data",
    )
    parser.add_argument(
        "filename",
        help="Name of the main taxonomy file, without extension",
        default="test_rdf_entries",
    )
    parser.add_argument(
        "external_files",
        nargs="*",
        help="Names of the external taxonomy files",
        default=[]
    )
    parser.add_argument(
        "-o", "--output_dir", nargs="?", help="Directory to save the output .ttl file", default="."
    )
    args = parser.parse_args()

    source_dir = args.source_dir
    main_file = args.filename
    filename = str(Path(source_dir, f"{main_file}.txt"))
    
    output_dir = args.output_dir
    scheme_id = main_file.replace("/", "_")
    external_filenames = [str(Path(source_dir, f"{external_file}.txt")) for external_file in args.external_files]

    graph = parse_to_rdf(filename, external_filenames=external_filenames, scheme_id=scheme_id)
    graph.serialize(destination=f"{output_dir}/{scheme_id}.ttl")
