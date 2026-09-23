# SPARQL Recipes

This document provides example SPARQL queries for common taxonomy checks.

## Get an inherited property

This type of query traverses up the parents of a concept to find the value of a property on the closest parent (or the concept itself).

This might be useful to establish whether a taxonomy entry is getting the correct value for a property from a parent or whether the property needs to be overridden at a lower level.

If multiple parents at the same level have a value for the property then the value from the alphabetically soonest parent is used.

```SPARQL
SELECT 
  ?concept 
  (IRI(STRBEFORE(STRAFTER(?winningKey, "|"), "|")) AS ?bestParent)
  (STRAFTER(STRAFTER(?winningKey, "|"), "|") AS ?propertyValue)
  ((xsd:integer(STRBEFORE(?winningKey, "|")) + 0) AS ?pathLength)
WHERE {
  # Layer 2: Find the absolute MIN winning key per ingredient across all parents
  {
    SELECT ?concept (MIN(?key) AS ?winningKey)
    WHERE {
      # Layer 1: Calculate depth and build packed key for each (concept, parent) pair
      {
        SELECT 
          ?concept
          (CONCAT(
            SUBSTR(CONCAT("0000", STR(COUNT(DISTINCT ?mid) - 1)), STRLEN(STR(COUNT(DISTINCT ?mid) - 1))),
            "|",
            STR(?parent),
            "|",
            STR(?propertyValue)
          ) AS ?key)
        WHERE {
          # Specify the type of taxonomy here
          ?concept a off:FoodIngredient .
          ?concept skos:broader* ?parent .

          # Specify the property you are interested in below:
          ?parent off:vegan ?propertyValue .
          
          ?concept skos:broader* ?mid .
          ?mid skos:broader* ?parent .
        }
        GROUP BY ?concept ?parent ?propertyValue
      }
    }
    GROUP BY ?concept
  }
}
ORDER BY ?concept
```

### How it works

The inner query selects all of the possible parents of a concept that have a value for the specified property (in this case `off:vegan`). It also navigates through all intermediate parent concepts to calculate the path length. The path length, parent identifier and property value are concatenated into a key.

The outer query then selects the minimum value of this key for each concept, unpacking the parts to give the parent id, path length and property value.

## Find Entries without Translations

The following query fetches all concepts that don't have a translation in the specified language:

```SPARQL
SELECT ?concept
WHERE {
  # 1. Match all target concepts (e.g. SKOS Concepts)
  ?concept a off:FoodIngredient .

  # 2. Exclude concepts that have a prefLabel matching the specific language code
  FILTER NOT EXISTS {
    ?concept skos:prefLabel ?label .
    FILTER(LANG(?label) = "fr") # Change "fr" to your desired language tag (e.g., "en", "de", "es")
  }
}
ORDER BY ?concept
```
