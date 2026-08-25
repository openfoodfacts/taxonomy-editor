# How to Structure Cross-references other Ontologies

## Context and Problem Statement

Our taxonomies express many concept that are also already expressed in other Ontologies. For example, the concept of a Vegan diet is referenced in:

* Ontology for Nutritional Studies (ONS) [vegan diet](http://purl.obolibrary.org/obo/ONS_1000021)
* FoodOn [vegan/vegetarian or suitability for vegan/vegetarian claim](http://purl.obolibrary.org/obo/FOODON_03510199)
* NCIT [Vegan Diet](http://purl.obolibrary.org/obo/NCIT_C15630)
* SNOMED [Vegan diet](http://snomed.info/id/1255165006)
* Schema.org [VeganDiet](https://schema.org/VeganDiet)

The above is an example of a "classification" when used in the context of a taxonomy like Ingredients, as many Ingredients will have a Vegan classification, i.e. a many to one relationship. However, we also define other properties, such as links to CIQUAL codes, where this is more of a "same as" or "similar to" relationship, i.e. one to one.

This document considers the general approach for linking to these external ontologies.

## Decision Drivers

* Our taxonomy ontologies should be easy to consume in their own right without the need to manually load multiple dependencies
* We may wish to apply our own labelling and translations to different concepts
* We want people consuming our taxonomies to be able to easily cross-reference them to their own data sets

## Considered Options

* Direct references to other ontologies
* Our own level of indirection

## Decision Outcome

Chosen option: Use "Our own level of indirection" when referencing a foreign item that classifies our item, i.e. many of our items will reference the same foreign item, e.g. `isVegan`. Use "Direct references to other ontologies" where there is more of a one to one relationship, e.g. when cross-referencing an ingredient to its CIQUAL code.

This gives us maximum flexibility to extend and translate our classification systems without introducing unnecessary levels of indirection.

## Consequences

We would retain our existing taxonomies even for generic concepts like languages, countries and allergens, adding cross-references where appropriate.

We would also need to generate our own ontologies for things like dietary preferences, where a taxonomy does not currently exist. We may choose to only include these in the RDF representation of our taxonomies or we may decide to create a "traditional" taxonomy file for each of these concepts.

## Pros and Cons of the Options

### Direct References

This would involve referencing the foreign ontology directly from our own item. For example, we might represent `vegan:en: maybe` with a triple like `ingredient:en-worcester-sauce off:maybe schema:VeganDiet` where `schema` is the namespace of the external schema.

* Good: Makes SPARQL queries simpler for consumers wanting to use the foreign ontology
* Good: Avoid duplication
* Neutral: May need to extend the foreign vocabulary for items we need that it does not include, e.g. `from_palm_oil:en`
* Bad: Limits the way we can express the relationship
* Bad: Foreign definition of the concept may not align with our own
* Bad: Difficult to add cross-references to more than one ontology

### Indirect References

Using the same structure as above we might represent the vegan status on an ingredient with a triple like `ingredient:en-worcester-sauce off:maybe off:vegan` and then define `off:vegan` ourselves to include the following statement `off:vegan skos:exactMatch schema:VeganDiet`

* Good: Allows maximum flexibility in defining the scope of our own classification system
* Good: Supports multiple cross-references and cross-referencing methods
* Bad: Additional join in SPARQL queries when linking to the foreign ontology
* Bad: May introduce some duplication with existing ontologies

