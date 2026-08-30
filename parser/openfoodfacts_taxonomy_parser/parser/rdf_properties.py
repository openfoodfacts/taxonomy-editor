from typing import Callable

from rdflib import OWL, RDF, RDFS, SKOS
from rdflib import XSD as RDF_XSD
from rdflib import Graph, Literal, Namespace, URIRef

ROOT = Namespace("https://openfoodfacts.org/data/taxonomies")
OFF = Namespace(f"{ROOT}/core#")
# This is not an official CIQUAL namespace, but seems to be the closest we've got
CIQUAL = Namespace("https://ico.iate.inra.fr/meatylab/origin_databases/2/foods/")
# These are not RDF resources but at least creates something clickable
AGRIBALYSE = Namespace("https://agribalyse.ademe.fr/app/aliments/")
WIKIDATA = Namespace("http://www.wikidata.org/entity/")

NAMESPACE_PREFIXES = {
    OFF: "off",
    CIQUAL: "ciqual",
    AGRIBALYSE: "agribalyse",
    WIKIDATA: "wd",
}


class PropertyDefinition:
    property: URIRef
    converter: Callable[[str], URIRef] | Namespace
    type: URIRef
    properties: list[tuple[URIRef, URIRef]]
    additional_triples: list[tuple[URIRef, URIRef, URIRef]]

    def __init__(
        self,
        property: URIRef,
        converter: Callable[[str], URIRef] | Namespace = None,
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
            self.converter[
                value.split()[0]
            ]  # When referencing URIs strip anything after whitespace, like comments
            if value and isinstance(self.converter, Namespace)
            else (
                self.converter(value)
                if isinstance(self.converter, Callable)
                else Literal(value, lang)
            )
        )
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
            if isinstance(self.converter, Namespace):
                prefix = NAMESPACE_PREFIXES.get(self.converter)
                if prefix:
                    graph.bind(prefix, self.converter)
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
            # graph.add((self.property, SKOS.altLabel, Literal(f"Added by {concept.fragment}")))
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
        # graph.add((property, SKOS.altLabel, Literal(f"Added by {concept.fragment}")))


PROPERTY_MAP = {
    "description": PropertyDefinition(SKOS.definition),
}


def exactMatchProperty(property_name, namespace):
    PROPERTY_MAP[property_name] = PropertyDefinition(
        OFF[toLowerCamelCase(property_name)],
        namespace,
        OWL.ObjectProperty,
        [(RDFS.subPropertyOf, SKOS.exactMatch)],
    )


def closeMatchProperty(property_name, namespace):
    PROPERTY_MAP[property_name] = PropertyDefinition(
        OFF[toLowerCamelCase(property_name)],
        namespace,
        OWL.ObjectProperty,
        [(RDFS.subPropertyOf, SKOS.closeMatch)],
    )


def externalAnnotationProperty(property_name):
    PROPERTY_MAP[property_name] = PropertyDefinition(
        OFF[toLowerCamelCase(property_name)],
        None,
        OWL.AnnotationProperty,
        [(RDFS.subPropertyOf, SKOS.altLabel)],
    )


def dietaryStatusProperty(property_name):
    is_uri = OFF[toLowerCamelCase(f"is_{property_name}")]
    not_uri = OFF[toLowerCamelCase(f"not_{property_name}")]
    maybe_uri = OFF[toLowerCamelCase(f"maybe_{property_name}")]
    status_uri = OFF[toLowerCamelCase(f"{property_name}_status")]
    label = property_name.title().replace("_", "")
    PROPERTY_MAP[property_name] = PropertyDefinition(
        OFF[toLowerCamelCase(property_name)],
        lambda value: {"yes": is_uri, "no": not_uri, "maybe": maybe_uri}.get(value.lower()),
        OWL.ObjectProperty,
        [(RDFS.range, status_uri)],
        [
            (status_uri, RDF.type, OWL.Class),
            (is_uri, RDF.type, OWL.Class),
            (is_uri, RDFS.subClassOf, status_uri),
            (is_uri, SKOS.prefLabel, Literal(f"Is {label}", "en")),
            (not_uri, RDF.type, OWL.Class),
            (not_uri, RDFS.subClassOf, status_uri),
            (not_uri, SKOS.prefLabel, Literal(f"Is not {label}", "en")),
            (maybe_uri, RDF.type, OWL.Class),
            (maybe_uri, RDFS.subClassOf, status_uri),
            (maybe_uri, SKOS.prefLabel, Literal(f"Might be {label}", "en")),
        ],
    )


exactMatchProperty("ciqual_food_code", CIQUAL)
closeMatchProperty("ciqual_proxy_food_code", CIQUAL)
externalAnnotationProperty("ciqual_food_name")
externalAnnotationProperty("ciqual_proxy_food_name")
exactMatchProperty("agribalyse_food_code", AGRIBALYSE)
closeMatchProperty("agribalyse_proxy_food_code", AGRIBALYSE)
externalAnnotationProperty("agribalyse_food_name")
externalAnnotationProperty("agribalyse_proxy_food_name")
dietaryStatusProperty("vegan")
dietaryStatusProperty("vegetarian")
# Note don't do anything special with Wikipedia links to retain different language links
exactMatchProperty("wikidata", WIKIDATA)
