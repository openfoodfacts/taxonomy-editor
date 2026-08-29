This project contains utilities for converting our taxonomies into RDF ontologies. The utility can be called as a libraryy or run from the command line following instructions in the [module](../parser/openfoodfacts_taxonomy_parser/parser/rdf_parser.py).

Decisions relating to how these ontologies are structured are documented [here](decisions/ontologies/README.md)

## TODO

Namespacing for taxonomies that vary by product type, e.g. food vs beauty ingredients.

Full property definitions for standard properties, including:

- Agribalyse codes
- USDA codes
- Wikidata links
- Wikipedia links

Coping with cross-references that don't go to the canonical id. e.g. "en: Amber IPA" references "en: India Pale Ale (IPA)" as a parent but the canonical id is "ca: Cervesa IPA"
