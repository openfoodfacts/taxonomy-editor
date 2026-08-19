from pathlib import Path
import re

from rdflib import RDF, SKOS, Graph, Literal, Namespace

from .taxonomy_parser import TaxonomyParser

OFF = Namespace("https://openfoodfacts.org/data/taxonomies/core#")

def parse_to_rdf(filename) -> Graph:
    """
    Parse a taxonomy file to RDF format.

    Args:
        filename (str): The path to the taxonomy file.

    Returns:
        rdflib.Graph: The RDF graph containing the parsed taxonomy.
    """
    taxonomy_parser = TaxonomyParser()
    taxonomy = taxonomy_parser.parse_file(filename)
    graph = Graph()
    
    # Create the core namespace prefix
    graph.bind("off", OFF)

    # Create a concept scheme for the taxonomy
    scheme_id = Path(filename).stem
    scheme_label = scheme_id.replace("_", " ").title()
    scheme = OFF[scheme_id]
    graph.add((scheme, RDF.type, SKOS.ConceptScheme))
    graph.add((scheme, SKOS.prefLabel, Literal(scheme_label, "en")))
    
    ns = Namespace(f"https://openfoodfacts.org/data/taxonomies/{scheme_id}#")
    graph.bind(scheme_id, ns)

    for node in taxonomy.entry_nodes:
        # As per decision document the language part is not used in the id
        concept = ns[node.id.split(":",1)[1]]
        graph.add((concept, RDF.type, SKOS.Concept))
        graph.add((concept, SKOS.inScheme, scheme))

        # Add labels
        for tag, values in node.tags.items():
            if match := re.search("tags_([^_]*)$", tag):
                lang = match.group(1)
                graph.add((concept, SKOS.prefLabel, Literal(values[0], lang)))
                
                for synonym in values[1:]:
                    graph.add((concept, SKOS.altLabel, Literal(synonym, lang)))


    graph.serialize(destination="debug.ttl")
    return graph