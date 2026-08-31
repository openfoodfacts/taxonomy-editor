import json
from typing import Callable
from urllib import request

from rdflib import OWL, RDF, RDFS, SKOS
from rdflib import XSD as RDF_XSD
from rdflib import Literal, Namespace, URIRef

from openfoodfacts_taxonomy_parser.parser.rdf_context import RdfContext
from openfoodfacts_taxonomy_parser.utils import normalize_text

ROOT = Namespace("https://openfoodfacts.org/data/taxonomies")
OFF = Namespace(f"{ROOT}/core#")
# This is not an official CIQUAL namespace, but seems to be the closest we've got
CIQUAL = Namespace("https://ico.iate.inra.fr/meatylab/origin_databases/2/foods/")
# These are not RDF resources but at least creates something clickable
AGRIBALYSE = Namespace("https://agribalyse.ademe.fr/app/aliments/")
WIKIDATA = Namespace("http://www.wikidata.org/entity/")
FOOD_GROUPS = Namespace(f"{ROOT}/food_groups#")
LANGUAGES = Namespace(f"{ROOT}/languages#")

NAMESPACE_PREFIXES = {
    OFF: "off",
    CIQUAL: "ciqual",
    AGRIBALYSE: "agribalyse",
    WIKIDATA: "wd",
    FOOD_GROUPS: "food_groups",
    LANGUAGES: "languages",
}

languages_taxonomy = None


class PropertyDefinition:
    property: URIRef
    namespace: Namespace
    converter: Callable[[RdfContext, str], URIRef]
    type: URIRef
    properties: list[tuple[URIRef, URIRef]]
    additional_triples: list[tuple[URIRef, URIRef, URIRef]]

    def __init__(
        self,
        property: URIRef,
        namespace: Namespace = None,
        converter: Callable[[RdfContext, str], URIRef] = None,
        type: URIRef = None,
        properties: list[tuple[URIRef, URIRef]] = None,
        additional_triples: list[tuple[URIRef, URIRef, URIRef]] = None,
    ):
        self.property = property
        self.converter = converter
        self.namespace = namespace
        self.type = type
        self.properties = properties or []
        self.additional_triples = additional_triples or []

    def add(
        self,
        context: RdfContext,
        value,
        lang: str,
    ):
        converted_value = self.converter(context, value) if self.converter else value

        if (self.property, None, None) not in context.graph:
            if self.namespace:
                prefix = NAMESPACE_PREFIXES.get(self.namespace)
                if prefix:
                    context.graph.bind(prefix, self.namespace)
            if self.type:
                context.graph.add((self.property, RDF.type, self.type))
                # Always add a domain
                context.graph.add((self.property, RDFS.domain, context.class_uri))
            if self.properties:
                for prop, obj in self.properties:
                    context.graph.add((self.property, prop, obj))
            if self.additional_triples:
                for triple in self.additional_triples:
                    context.graph.add(triple)

        values = converted_value if isinstance(converted_value, list) else [converted_value]
        for graph_value in values:
            if not graph_value:
                context.logger.warning(
                    "Unknown value on {0} for property {1}: {2}".format(
                        context.concept.fragment, self.property.fragment, value
                    )
                )
                # Add the raw value to the graph anyway
                context.graph.add((context.concept, self.property, Literal(value, lang)))
                return

            context.graph.add(
                (
                    context.concept,
                    self.property,
                    (
                        graph_value
                        if isinstance(graph_value, URIRef)
                        else (
                            # We remove everything after the first whitespace for namespaced URIs
                            self.namespace[graph_value.split()[0]]
                            if self.namespace
                            else Literal(graph_value, lang)
                        )
                    ),
                )
            )


def toLowerCamelCase(snake_str):
    first, *others = snake_str.split("_")
    return "".join([first.lower(), *map(str.title, others)])


def normalized_id(tag):
    lc, main_tag = tag.strip().split(":", 1)
    normalized_main_tag = normalize_text(main_tag, lc)
    return (normalized_main_tag, lc)


def canonical_id(context, tag):
    normalized_main_tag, lc = normalized_id(tag)
    tag_id = f"tags_ids_{lc}"
    matching_nodes = [
        node
        for node in context.taxonomy.entry_nodes
        if normalized_main_tag in node.tags.get(tag_id, [])
    ]
    if matching_nodes:
        if len(matching_nodes) > 1:
            context.logger.warning(f"{normalized_main_tag} is ambiguous")
        return matching_nodes[0].id.split(":", 1)[1]
    context.logger.warning(f"{normalized_main_tag} not found")
    return normalized_main_tag


def get_language(context, value):
    global languages_taxonomy
    if not languages_taxonomy:
        languages_taxonomy = json.loads(
            request.urlopen("https://static.openfoodfacts.org/data/taxonomies/languages.json")
            .read()
            .decode("utf-8")
        )
    context.graph.bind(NAMESPACE_PREFIXES[LANGUAGES], LANGUAGES)
    value = value.strip()
    matches = [
        id
        for id, language in languages_taxonomy.items()
        if value == language.get("language_code_2", {}).get("en")
    ]
    if not matches:
        matches = [
            id
            for id, language in languages_taxonomy.items()
            if value == language.get("language_code_3", {}).get("en")
        ]

    if not matches:
        context.logger.warning(f"Language {value} not found")
        return value

    return normalized_id(matches[0])[0]


LANGUAGE_LESS_PROPERTIES = [
    "country_code_2",
    "country_code_3",
    "langauge_code_2",
    "langauge_code_3",
]


def add_default_property(context: RdfContext, property_name: str, value: str, lang: str):
    # Unknown property name
    # Convert property names to lowerCamelCase for RDF representation as this follows industry norms
    property = OFF[toLowerCamelCase(property_name)]
    graph_value = (
        Literal(value) if property_name in LANGUAGE_LESS_PROPERTIES else Literal(value, lang)
    )
    context.graph.add((context.concept, property, graph_value))

    # Add the property to the class definition if it hasn't been added yet
    if (property, RDF.type, RDF.Property) not in context.graph:
        context.graph.add((property, RDF.type, RDF.Property))
        context.graph.add((property, RDFS.domain, context.class_uri))
        context.graph.add((property, RDFS.range, RDF_XSD.string))
        # graph.add((property, SKOS.altLabel, Literal(f"Added by {concept.fragment}")))


PROPERTY_MAP = {
    "description": PropertyDefinition(SKOS.definition),
    "plant_alternative": PropertyDefinition(
        OFF.plantAlternative,
        None,
        lambda context, tag: context.namespace[canonical_id(context, tag)],
        OWL.ObjectProperty,
        [(RDFS.subPropertyOf, SKOS.related)],
    ),
    "opposite": PropertyDefinition(
        OFF.opposite,
        None,
        lambda context, tags: [
            context.namespace[canonical_id(context, tag)] for tag in tags.split(",")
        ],
        OWL.ObjectProperty,
        [(RDFS.subPropertyOf, SKOS.related)],
    ),
    "food_groups": PropertyDefinition(
        OFF.foodGroup,
        FOOD_GROUPS,
        lambda context, tags: [normalized_id(tag)[0] for tag in tags.split(",")],
        OWL.ObjectProperty,
        [(RDFS.subPropertyOf, SKOS.broader), (RDFS.range, OFF.FoodGroup)],
    ),
    "language_codes": PropertyDefinition(
        OFF.language,
        LANGUAGES,
        lambda context, tags: [get_language(context, tag) for tag in tags.split(",")],
        OWL.ObjectProperty,
        [(RDFS.subPropertyOf, SKOS.related), (RDFS.range, OFF.Language)],
    ),
}


def exactMatchProperty(property_name, namespace):
    PROPERTY_MAP[property_name] = PropertyDefinition(
        OFF[toLowerCamelCase(property_name)],
        namespace,
        None,
        OWL.ObjectProperty,
        [(RDFS.subPropertyOf, SKOS.exactMatch)],
    )


def closeMatchProperty(property_name, namespace):
    PROPERTY_MAP[property_name] = PropertyDefinition(
        OFF[toLowerCamelCase(property_name)],
        namespace,
        None,
        OWL.ObjectProperty,
        [(RDFS.subPropertyOf, SKOS.closeMatch)],
    )


def externalAnnotationProperty(property_name):
    PROPERTY_MAP[property_name] = PropertyDefinition(
        OFF[toLowerCamelCase(property_name)],
        None,
        None,
        OWL.AnnotationProperty,
        [(RDFS.subPropertyOf, SKOS.altLabel)],
    )


def dietaryStatusProperty(property_name):
    is_uri = OFF[toLowerCamelCase(f"is_{property_name}")]
    not_uri = OFF[toLowerCamelCase(f"not_{property_name}")]
    maybe_uri = OFF[toLowerCamelCase(f"maybe_{property_name}")]
    status_uri = OFF[toLowerCamelCase(f"{property_name}_status")]
    PROPERTY_MAP[property_name] = PropertyDefinition(
        OFF[toLowerCamelCase(property_name)],
        None,
        lambda context, value: {
            "yes": is_uri,
            "no": not_uri,
            "maybe": maybe_uri,
        }.get(value.lower()),
        OWL.ObjectProperty,
        [(RDFS.range, status_uri)],
        [
            (status_uri, RDF.type, OWL.Class),
            (is_uri, RDF.type, OWL.Class),
            (is_uri, RDFS.subClassOf, status_uri),
            (is_uri, SKOS.prefLabel, Literal("Yes", "en")),
            (not_uri, RDF.type, OWL.Class),
            (not_uri, RDFS.subClassOf, status_uri),
            (not_uri, SKOS.prefLabel, Literal("No", "en")),
            (maybe_uri, RDF.type, OWL.Class),
            (maybe_uri, RDFS.subClassOf, status_uri),
            (maybe_uri, SKOS.prefLabel, Literal("Maybe", "en")),
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
dietaryStatusProperty("from_palm_oil")
# Note don't do anything special with Wikipedia links to retain different language links
exactMatchProperty("wikidata", WIKIDATA)
