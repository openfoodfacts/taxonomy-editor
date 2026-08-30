# How to Generate Unique URLs for our Taxonomy Entries

## Context and Problem Statement

Our current taxonomies generate a canonical identifier from the first label of the entry. For example `en: Plant Milks, alternative milks, non-dairy milk drinks` would have a canonical id of `en:plant-milks`. Should we use this identifier in our ontologies?

We also need to consider how to generate the prefix / base URL for our items in order to make them globally unique.

## Decision Drivers

- it should be easy to match the ontology entry with our existing taxonomy item
- identifiers must ne unique
- identifiers should ideally be immutable
- identifiers with prefix should be reasonably compact

## Considered Options

There are two aspects to this decision:

### What to use as the URL prefix

Options considered:

- use a single `off:` prefix for all of our items in all taxonomies
- have separate prefixes for each taxonomy, prefixed with `off`, e.g. `off-ingredients:`
- have separate prefixes for each taxonomy without an `off` prefix, e.g. `ingredients:`

### How to identify the specific Item (URL suffix)

Options considered:

- use the existing canonical identifier
- use the existing identifier, replacing the colon with a dash
- use the existing identifier without the country code
- generate a new, immutable, identifier

## Decision Outcome

Chosen option: "use the taxonomy name" for the prefix and "use the existing identifier without the country code" for the suffix (subject to checking for duplicates in our existing taxonomies).

The `off:` prefix will also be used for core URLs that are not specific to any one taxonomy.

## Pros and Cons of the Options

### Use a single `off` prefix for all items

- Good: Less prefixes for other consumers to worry about
- Neutral: Care must be taken to ensure that user-generated identifiers do not clash with our core vocabulary
- Bad: The taxonomy name will need to be incorporated into the identifier suffix to ensure uniqueness

### Use a prefix for each taxonomy, prefixed with `off-`

- Good: Clearly identifies items from our own ontologies
- Good: Less likely to clash with other ontology prexies
- Bad: More prefixes
- Bad: Slightly verbose

### Use the taxonomy name as the prefix, e.g. `ingredients:`

- Good: Creates the most compact id
- Neutral: Consumers can use their own prefix if desired
- Bad: May clash with other industry standard prefixes

### Use the existing canonical identifier

In this case the full URI for an item might be something like: `https://openfoodfacts.org/data/taxonomies/ingredients#en:milk-powder`

- Good: Works with our existing APIs and facets pages
- Good: Aligns with our existing canonical identifiers
- Neutral: Users may feel they need to escape the colon, which is not necessary
- Bad: Some tools, such as RDFlib, don't apply prefixes if the URI contains a colon
- Bad: Currently our identifiers can change if the preferred label for the first language is updated

### Use the existing identifier, replacing the colon with a dash

In this case the full URI for an item might be something like: `https://openfoodfacts.org/data/taxonomies/ingredients#en-milk-powder`

- Good: No confusion about escaping the colon
- Good: Intuitively similar to our existing identifier
- Bad: Doesn't work with our existing APIs or facets pages
- Bad: Can still change

### Use the existing identifier without the country code

In this case the full URI for an item might be something like: `https://openfoodfacts.org/data/taxonomies/ingredients#milk-powder`

- Good: No confusion about escaping the colon
- Good: Intuitively similar to our existing identifier
- Good: Should work with our APIs and facets pages
- Good: Identifier will not need to change if we later introduce a new, immutable, `xx:` identifier
- Bad: Could introduce duplicates

### Generate a new, immutable, identifier

In this case the full URI for an item might be something like: `https://openfoodfacts.org/data/taxonomies/ingredients#0a7f1bc8-32b4-43cb-b56e-69f9e30a5521`

- Good: No confusion about escaping the colon
- Good: Globally unique and immutable
- Bad: Won't work with our current APIs and facets pages
- Bad: Does not correlate with our existing taxonomies
- Bad: Difficult for humans to generate new identifiers
