import json
import os
from urllib import request

from rdflib import Graph, Namespace


NS_ROOT = Namespace("https://openfoodfacts.org/data/taxonomies")
OFF = Namespace(f"{NS_ROOT}/core#")

TAXONOMY_JSON_ROOT = os.environ.get("TAXONOMY_JSON_ROOT", "https://static.openfoodfacts.org/data/taxonomies")

NAMESPACE_PREFIXES = {
    OFF: "off",
}


def addTaxonomyNamespace(name):
    return addNamespace(name, f"{NS_ROOT}/{name}#")

def addNamespace(prefix, uri):
    ns = Namespace(uri)
    NAMESPACE_PREFIXES[ns] = prefix
    return ns

def bindNamespace(graph: Graph, ns: Namespace):
    prefix = NAMESPACE_PREFIXES.get(ns)
    if prefix:
        graph.bind(prefix, ns)
        
def getTaxonomyJson(name):
    return json.loads(
        request.urlopen(f"{TAXONOMY_JSON_ROOT}/{name}.json")
        .read()
        .decode("utf-8")
    )
