This project contains utilities for converting our taxonomies into RDF ontologies. The utility can be called as a library or run from the command line following instructions in the [module](../parser/rdf_export/rdf_parser.py).

Decisions relating to how these ontologies are structured are documented [here](decisions/ontologies/README.md)

## Browsing the Taxonomies

The converted taxonomies have been uploaded to a tool called [ShowVoc](https://showvoc.uniroma2.it/doc/user/) and can be accessed by following [this](https://taxonomies.openfoodfacts.net/showvoc/#/datasets) link.

The [Datasets view](https://showvoc.uniroma2.it/doc/user/datasets.jsf) shows an entry for each taxonomy. Taxonomies that are unique to a specific product type are prefixed with that product type, e.g. food_ingredients.

Once you have clicked on the dataset you require you will be directed to the [Data view page](https://showvoc.uniroma2.it/doc/user/dataset.jsf) for that dataset. Each entry in the taxonomy is represented as a Concept in a hierarchy based on the parent/child relationships defined in the taxonomy.

You will notice that initially each entry is displayed using the preferred label for every language. You can change you language preferences by clicking on the [globe](https://showvoc.uniroma2.it/doc/user/data_view.jsf#the_data_structure_view) icon. Once you have done this, click the refresh icon to re-load just the languages you want. You can also choose to render by the canonical id of the entry by toggling the "A" button.

You will notice that the canonical id we are using does not include the language prefix. The decision for this is documented [here](decisions/ontologies/url-naming.md). This results in a few duplicates in some of the taxonomies which we hope to address in the data.

Once you click on an entry you will see all of the information about that entry in the right hand [Resource view](https://showvoc.uniroma2.it/doc/user/data_view.jsf#the_resource_view).

Each taxonomy is stored as a Concept Scheme. Most Datasets will only show one concept scheme, except for origins and food_ingredients, which show a combination of all of the taxonomies that are combined together when that taxonomy is used in practice.

The term Broader on an entry shows the parent(s) of that entry. You will again notice that the Preferred Label and Alternative Label (synonyms) are shown in all languages. You can again choose to only see specific languages by clicking the [cog icon](https://showvoc.uniroma2.it/doc/user/data_view.jsf#resource_view_settings) in this panel to change the rendering settings.

Other properties are also listed against the entry. The general naming convention in the underlying RDF files is to store the property name in lowerCamelCase, but in ShowVoc this will be rendered in Title Case.

Initially most of the properties are being rendered as simple strings, but in some cases we are applying specific logic. For example, if you look at [this](https://taxonomies.openfoodfacts.net/showvoc/#/datasets/food_ingredients/1.0.0/data?resId=https:%2F%2Fopenfoodfacts.org%2Fdata%2Ftaxonomies%2Ffood_ingredients%23couscous) ingredient you will see that the Ciqual Food Code and Wikidata reference are saved as links to an external ontology (in these specific cases the links don't work due to a [known issue](#external-links-give-an-error)). You may also notice that flags like Vegan and Vegetarian are defined as a structure property.

Some properties, like Food Group in this [food category](https://taxonomies.openfoodfacts.net/showvoc/#/datasets/food_categories/1.0.0/data?resId=https:%2F%2Fopenfoodfacts.org%2Fdata%2Ftaxonomies%2Ffood_categories%23christmas-puddings) have been configured to link to the related taxonomy. This needs to be done in a number of other places. If you notice a link that is just being store as text then please flag this up.

## Checking Properties

On each taxonomy you will see a [Property tab](https://taxonomies.openfoodfacts.net/showvoc/#/datasets/labels/1.0.0/data?resId=https:%2F%2Fopenfoodfacts.org%2Fdata%2Ftaxonomies%2Fcore%23packaging). This lists all of the known properties for this taxonomy. You will find the Open Food Facts properties towards the bottom of this list, prefixed with `off:`. In some cases they may also appear under another property hierarchy, such as [ciqualFoodCode](https://taxonomies.openfoodfacts.net/showvoc/#/datasets/food_categories/1.0.0/data?resId=https:%2F%2Fopenfoodfacts.org%2Fdata%2Ftaxonomies%2Fcore%23ciqualFoodCode).

You may find that some property names indicate incorrect spelling, e.g. [ciqualFoodProxyCode](https://taxonomies.openfoodfacts.net/showvoc/#/datasets/food_categories/1.0.0/data?resId=https:%2F%2Fopenfoodfacts.org%2Fdata%2Ftaxonomies%2Fcore%23ciqualFoodProxyCode) instead of `ciqualProxyFoodCode`. You can find these rogue entries by simply searching the original taxonomy `.txt` file (converting back to snake_case) or you could use the [SPARQL](https://taxonomies.openfoodfacts.net/showvoc/#/datasets/food_categories/1.0.0/sparql) tab to run a query on the actual taxonomy, e.g. 

```
SELECT * WHERE {
    ?s off:ciqualFoodProxyCode ?o .
} LIMIT 10
```

## Global Synonyms and Stopwords

These are stored as properties on the actual [Concept Scheme](https://taxonomies.openfoodfacts.net/showvoc/#/datasets/food_ingredients/1.0.0/data?resId=https:%2F%2Fopenfoodfacts.org%2Fdata%2Ftaxonomies%2Fcore%23food_ingredients).

## Making Corrections

At the moment, any corrections need to be made in the core taxonomy files using the normal Pull Request process. We will periodically refresh the data in ShowVoc as these updates are merged.

## Known Issues

### External Links Give an Error

ShowVoc does not behave like a normal browser when it queries Wikidata entries and Wikidata therefore rejects these requests with an error like `Server returned HTTP response code: 403 for URL:`. You can manually see the external references by copying the URL and pasting it into a new browser tab.

In the case of Agribalyse the data is not published as a true OWL ontology, so you also have to manually copy and paste the URL to see the relevant web page.


## TODO

This is a rough list of known tasks that need to be completed. Please feel free to identify others:

Full property definitions for standard properties, including:

- USDA codes
- Nova classifications

Cross-referencing between taxonomies, e.g. expected ingredients in categories

Add documentation and international labels to the properties

Figure out a way to get links working for things like CIQUAL, Agribalyse and Wikidata

Add a range to ObjectProperties that reference own taxonomy

Decision document on external taxonomies

Comments on why we encode URLs

Stopwords and synonyms aren't being populated for external taxonomies