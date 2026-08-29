from rdflib import OWL, RDF, RDFS, SKOS
from rdflib import XSD as RDF_XSD
from rdflib import Graph, Literal, Namespace, URIRef

ROOT = Namespace("https://openfoodfacts.org/data/taxonomies")
OFF = Namespace(f"{ROOT}/core#")
CIQUAL = Namespace("https://ico.iate.inra.fr/meatylab/origin_databases/2/foods/")


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
        graph_value = self.converter(value) if self.converter else Literal(value, lang)
        if graph_value is None:
            logger.warning(
                "Unknown value on {0} for property {1}: {2}".format(
                    concept.fragment, self.property.fragment, value
                )
            )
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


def toLowerCamelCase(snake_str):
    first, *others = snake_str.split("_")
    return "".join([first.lower(), *map(str.title, others)])


def add_default_property(
    graph: Graph, class_uri: URIRef, concept: URIRef, property_name: str, value: str, lang: str
):
    # Unknown property name
    # Convert property names to lowerCamelCase for RDF representation as this follows industry norms
    property = OFF[toLowerCamelCase(property_name)]
    graph.add((concept, property, Literal(value, lang)))

    # Add the property to the class definition if it hasn't been added yet
    if (property, RDF.type, RDF.Property) not in graph:
        graph.add((property, RDF.type, RDF.Property))
        graph.add((property, RDFS.domain, class_uri))
        graph.add((property, RDFS.range, RDF_XSD.string))


PROPERTY_MAP = {
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
