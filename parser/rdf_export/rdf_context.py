from rdflib import Graph, Namespace, URIRef

from openfoodfacts_taxonomy_parser.parser.logger import ParserConsoleLogger
from openfoodfacts_taxonomy_parser.parser.taxonomy_parser import Taxonomy


class RdfContext:
    taxonomy: Taxonomy
    graph: Graph
    namespace: Namespace
    logger: ParserConsoleLogger
    class_uri: URIRef
    concept: URIRef

    def __init__(
        self,
        taxonomy: Taxonomy,
        graph: Graph,
        namespace: Namespace,
        logger: ParserConsoleLogger,
        class_uri: URIRef,
    ):
        self.taxonomy = taxonomy
        self.graph = graph
        self.namespace = namespace
        self.logger = logger
        self.class_uri = class_uri
