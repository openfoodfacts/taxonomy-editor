# Should we create a Class for each of our Taxonomies?

## Context and Problem Statement

In SKOS, every entry is a Concept which belongs to a Concept Scheme. The Concept Scheme aligns well with our idea of a taxonomy, but should we also create a Class for each taxonomy / concept scheme?

## Decision Drivers

* Ontologies should be easy to maintain
* Compatible with most ontology editing tools

## Considered Options

* No class
* Explicit class
* Infer class

## Decision Outcome

Chosen option: "Explicit class", because it has maximum compatibility with standard tooling without explicit configuration.

### Confirmation

Compliance with SHACL rules can be tested before taxonomy updates are committted.

## Pros and Cons of the Options

### No Class

In this case no class would be created and the taxonomy entry would just be a SKOS Concept in a Concept Scheme corresponding to the taxonomy name.

For example:

```turtle
@prefix off: <https://openfoodfacts.org/data/taxonomies/core#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

# Concept Scheme
off:ingredients a skos:ConceptScheme;
    skos:prefLabel "Ingredients"@en .

# An instance
ingredients:en-fruit a skos:Concept;
    skos:inScheme off:ingredients;
    skos:topConceptOf off:ingredients;
    skos:prefLabel "fruit"@en;
```

* Good: Simple approach
* Bad: Tools like VocBench won't suggest suitable properties, based on domain, when adding / editing entries

### Explicit Class

In this option, a Class would be created for every Taxonomy, and every item in the taxonomy would have to be a member of this class. This could be enforced with SHACL rule.

For example:

```turtle
@prefix off: <https://openfoodfacts.org/data/taxonomies/core#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .

# Concept Scheme
off:ingredients a skos:ConceptScheme;
    skos:prefLabel "Ingredients"@en .

# Class definition
off:Ingredient rdfs:subClassOf skos:Concept ;
    rdfs:label "A specific ingredient"@en .

# SHACL constraint    
off:EnforceSchemeClassShape a sh:NodeShape ;
    sh:targetSubjectsOf skos:inScheme ; 

    sh:sparql [
        a sh:SPARQLConstraint ;
        sh:message "Ingredient concepts must be an instance of the Ingredient class." ;
        sh:select """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX off: <https://openfoodfacts.org/data/taxonomies/core#>

            SELECT $this WHERE {
                $this skos:inScheme off:ingredients .
                FILTER NOT EXISTS { $this rdf:type off:Ingredient }
            }
        """ ;
    ] .

# An instance
ingredients:en-fruit a off:Ingredient;
    skos:inScheme off:ingredients;
    skos:topConceptOf off:ingredients;
    skos:prefLabel "fruit"@en;
```

* Good: Can define expected properties (and their constraints) using `rdfs:domain` and `rdfs:range`, supporting auto-suggest in editing tools
* Good: No reasoning required to determine class membership
* Bad: Users must remember to make all entries an instance of this class
* Bad: Tools like VocBench don't enforce SHACL rules by default

### Inferred Class

In this option, a Class would be created for every Taxonomy, but membership of this class would be inferred by an `owl:equivalentClass` statement or a SHACL rule based on membership of the Concept Scheme so there would no need to explicitly declare the class membership.

For example:

```turtle
@prefix off: <https://openfoodfacts.org/data/taxonomies/core#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# Concept Scheme
off:ingredients a skos:ConceptScheme;
    skos:prefLabel "Ingredients"@en .

# Class definition
off:Ingredient rdfs:subClassOf skos:Concept ;
    rdfs:label "A specific ingredient"@en .

# Define off:Ingredient to anything in off:ingredients scheme
off:Ingredient owl:equivalentClass [
    a owl:Restriction ;
    owl:onProperty skos:inScheme ;
    owl:hasValue off:ingredients
] .

# An instance
ingredients:en-fruit a skos:Class;
    skos:inScheme off:ingredients;
    skos:topConceptOf off:ingredients;
    skos:prefLabel "fruit"@en;
```

* Good: No redundancy
* Good: Can define expected properties (and their constraints) using `rdfs:domain` and `rdfs:range`, supporting auto-suggest in editing that support class inference
* Bad: Tools must be configured with an appropriate reasoner for this to work
