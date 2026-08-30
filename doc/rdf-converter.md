This project contains utilities for converting our taxonomies into RDF ontologies. The utility can be called as a libraryy or run from the command line following instructions in the [module](../parser/openfoodfacts_taxonomy_parser/parser/rdf_parser.py).

Decisions relating to how these ontologies are structured are documented [here](decisions/ontologies/README.md)

## TODO

Full property definitions for standard properties, including:

- USDA codes

Deal with taxonomies that are merged together, e.g. ingredients includes additives, vitamins, minerals, etc.

Cross-referencing between taxonomies, e.g. expected ingredients in categories

Add documentation and international labels to the properties

Figure out a way to get links working for things like CIQUAL, Agribalyse and Wikidata

