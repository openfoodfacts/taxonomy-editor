# Base Vocabulary for Taxonomies

## Context and Problem Statement

There are a number of different core vocabularies that we could use as the basis for our taxonomies.

## Decision Drivers

* Supports inheritance for item properties
* Visualizes well in standard tooling
* Suitable for crowd-sourced data

## Considered Options

* [Web Ontology Language (OWL)](https://en.wikipedia.org/wiki/Web_Ontology_Language)
* [Simple Knowledge Organization System (SKOS)](https://en.wikipedia.org/wiki/Simple_Knowledge_Organization_System)
* Our own lightweight [Resource Description Framework (RDF)](https://en.wikipedia.org/wiki/Resource_Description_Framework) vocabulary and [RDF Schema (RDFS)](https://en.wikipedia.org/wiki/RDF_Schema)

## Decision Outcome

We decided to use SKOS as the foundation for our taxonomies as it is more flexible for crowd-sourced data but still has accepted methods for "inheritance" and propagation of properties and has good tooling support.

However, we will also supplement this with our own RDF Schema to define expected properties and allowable values, potentially enforceable with [SHACL](https://en.wikipedia.org/wiki/SHACL) rules.

## Pros and Cons of the Options

### OWL

This is the vocabulary used by [FoodOn](https://foodon.org/) and provides a very rich, but rigid structure for expressing classes and relationships.

* Good: Rigid structure is good for validation
* Good: Widely supported in common RDF tools
* Bad: Strict inheritance of base class properties makes it difficult to deal with properties that change in descendants, e.g. milk is vegetarian, whilst whey (derived from milk) may not be depending on the renet used.
* Bad: Rigid structure may make it harder to obtain new contributions

### SKOS

This vocabulary is mainly designed for taxonomies and thesauri so would seem a natural fit. It is also used by [FoodEx2](https://www.efsa.europa.eu/en/data/data-standardisation) which is widely used by food researchers.

* Good: Supports hierarchy (`broader` and `narrower`) without the rigidity of OWL
* Good: Widely supported in common RDF tools
* Good: More relaxed rules, so easier for crowd-sourcing
* Neutral: May need to add further validation, e.g. [Shapes Constraint Language (SHACL)](https://en.wikipedia.org/wiki/SHACL) to enforce important rules
* Neutral: Will require thorough documentation on how to determine inherited properties

### Lightweight RDF and RDFS

* Good: Maximum flexibility to define our own structure
* Bad: Not reusing existing standards
* Bad: Will require customization of standard tooling to visualize hierarchies
