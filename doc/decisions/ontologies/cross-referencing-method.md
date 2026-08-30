# How to Declare Cross-references other Ontologies

## Context and Problem Statement

There are many different ways we can use to assert a relationship between an item in one of our ontologies and a foreign class or instance. This include:

- skos:exactMatch
- skos:closeMatch
- rdfs:seeAlso
- owl:subpropertyOf
- schema:sameAs
- oboInOwl:hasDbXref

## Decision Drivers

- Cross-references should clearly express the nature of the relationship
- Cross-references should not have undesirable side-effects
- Techniques should have maximum compatibility with existing tooling

## Considered Options

- Use existing SKOS relationships
- Use the approach that matches the vocabulary of the target
- Define a unique property for each type of relationship

## Decision Outcome

Chosen option: "Define our own unique properties" for links to other ontologies, because this provides maximum expressiveness and control. However, we would still use standard `skos:broader` / `skos:narrower` to define parent child relationships within our own taxonomies to maximize compatibility with existing SKOS tooling.

## Unresolved Issues

There is no "original" CIQUAL ontology, although CIQUAL terms are included in an [ontology](https://entrepot.recherche.data.gouv.fr/dataset.xhtml?persistentId=doi:10.15454/6CEYU3) that links CIQUAL to LanguaL. However, in this case each CIQUAL entry is defined as a generic `owl:Class`, there is no overarching class for CIQUAL items. Hence, the `rdfs:range` on our property could only be `owl:Class` which would not limit us to CIQUAL items.

## Pros and Cons of the Options

### Use existing SKOS relationships

In addition to using `skos:broader` / `skos:narrower` to represent parent / child relationships we would also use SKOS terms like `skos:exactMatch` and `skos:closeMatch` to link with other ontologies. `skos:closeMatch`, for example, could be used when linking to CIQUAL proxy codes.

- Good: Will be most familiar to existing users of SKOS
- Good: Well understood semantics
- Good: Integrates well with existing tooling
- Bad: Can introduce [punning](https://www.michaeldebellis.com/post/puns_in_owl_the_whys_and_hows) when referencing non-SKOS ontologies, which may have undesirable side-effects
- Bad: Does not provide a way to assert expected relationships and the target for those relationships

### Match the vocabulary of the target

In this option, SKOS would be used when referencing another SKOS ontology or where the target is an individual (rather than a class), but for other vocabularies, like when referencing an OWL class, a more appropriate property would be used.

In cases where only very generic properties, like `rdfs:seeAlso`, we would create our own sub-properties to provide a more expressive relationship, e.g. `off:closeMatch rdfs:subPropertyOf rdfs:seeAlso`

- Good: Does not introduce any unintended side-effects
- Good: Retains expressiveness
- Bad: May be difficult for users to know which property to use
- Bad: Does not provide a way to assert expected relationships and the target for those relationships

### Define unique properties

Rather than using generic properties to describe relationships we would create a separate property for each specific relationship, e.g. `off:ciqualCode`, `off:ciqualProxyCode`. These would be sub-properties of the appropriate property type for the target vocabulary.

- Good: Allows us to define which properties are expected for each taxonomy class and what ontology should be referenced
- Good: Integrates will with auto-suggest features of existing tooling
- Good: Allows us to easily enforce rules on cardinality, e.g. an Ingredient can only link ot one CIQUAL code
- Bad: Adds many more property types
- Bad: Generic tooling when performing standard tasks, like adding a child to a SKOS Concept, won't know to use our properties
