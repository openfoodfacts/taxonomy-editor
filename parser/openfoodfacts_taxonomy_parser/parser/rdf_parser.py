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

from rdflib import OWL, RDF, RDFS, SKOS, XSD as RDF_XSD, Graph, Literal, Namespace

from openfoodfacts_taxonomy_parser.parser.logger import ParserConsoleLogger

from .taxonomy_parser import TaxonomyParser

OFF = Namespace("https://openfoodfacts.org/data/taxonomies/core#")
CIQUAL = Namespace("https://ico.iate.inra.fr/meatylab/origin_databases/2/foods/")

inflect_engine = inflect.engine()

def toLowerCamelCase(snake_str):
    first, *others = snake_str.split('_')
    return ''.join([first.lower(), *map(str.title, others)])

def parse_to_rdf(filename, logger = None) -> Graph:
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
    graph.bind("off", OFF)

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
        concept = ns[node.id.split(":",1)[1]]
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
            parent_concept = ns[parent[0].split(":",1)[1]]
            graph.add((concept, SKOS.broader, parent_concept))

        if not node.parent_tags:
            graph.add((concept, SKOS.topConceptOf, scheme))
            
        # Properties
        for property_tag, value in node.properties.items():
            parts = property_tag.rsplit("_", 1) # Extract the language suffix
            property_name = parts[0][5:] # Remove the "prop_" prefix
            if property_name == "description":
                graph.add((concept, SKOS.definition, Literal(value, parts[1])))
            elif property_name == "ciqual_food_code":
                # Add CIQUAL definitions to the graph if they aren't there
                if (OFF.ciqualFoodCode, None, None) not in graph:
                    graph.bind("ciqual", CIQUAL)
                    graph.add((OFF.ciqualFoodCode, RDF.type, OWL.ObjectProperty))
                    graph.add((OFF.ciqualFoodCode, RDFS.subPropertyOf, SKOS.exactMatch))
                    graph.add((OFF.ciqualFoodCode, RDFS.domain, OFF[class_name]))
                    # Note can't add a range as CIQUAL codes do not share a common ancestor
                graph.add((concept, OFF.ciqualFoodCode, CIQUAL[value]))
            elif property_name == "ciqual_food_name":
                if (OFF.ciqualFoodName, None, None) not in graph:
                    graph.add((OFF.ciqualFoodName, RDF.type, OWL.AnnotationProperty))
                    graph.add((OFF.ciqualFoodName, RDFS.subPropertyOf, SKOS.altLabel))
                    graph.add((OFF.ciqualFoodName, RDFS.domain, OFF[class_name]))
                graph.add((concept, OFF.ciqualFoodName, Literal(value, parts[1])))
            elif property_name == "ciqual_proxy_food_code":
                # Add CIQUAL definitions to the graph if they aren't there
                if (OFF.ciqualProxyFoodCode, None, None) not in graph:
                    graph.bind("ciqual", CIQUAL)
                    graph.add((OFF.ciqualProxyFoodCode, RDF.type, OWL.ObjectProperty))
                    graph.add((OFF.ciqualProxyFoodCode, RDFS.subPropertyOf, SKOS.closeMatch))
                    graph.add((OFF.ciqualProxyFoodCode, RDFS.domain, OFF[class_name]))
                    # Note can't add a range as CIQUAL codes do not share a common ancestor
                graph.add((concept, OFF.ciqualProxyFoodCode, CIQUAL[value]))
            elif property_name == "ciqual_proxy_food_name":
                if (OFF.ciqualProxyFoodName, None, None) not in graph:
                    graph.add((OFF.ciqualProxyFoodName, RDF.type, OWL.AnnotationProperty))
                    graph.add((OFF.ciqualProxyFoodName, RDFS.subPropertyOf, SKOS.altLabel))
                    graph.add((OFF.ciqualProxyFoodName, RDFS.domain, OFF[class_name]))
                graph.add((concept, OFF.ciqualProxyFoodName, Literal(value, parts[1])))
            else:
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
