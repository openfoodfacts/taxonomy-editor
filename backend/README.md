# Taxonomy Editor API

This is the main Python API used by the React frontend, to interface with the Neo4J database.

## Requirements

- [FastAPI](https://github.com/tiangolo/fastapi)
- [openfoodfacts_taxonomy_parser](../parser/openfoodfacts_taxonomy_parser/)
- [Neo4J Python Driver](https://github.com/neo4j/neo4j-python-driver)
- [PyGithub](https://github.com/PyGithub/PyGithub)

## Setup Dev Environment

See [this guide](../doc/introduction/setup-dev.md) for more information.

## Check it!

After following the steps in the guide, the API should be available at the URL `http://api.taxonomy.localhost:8091`.

You will see the following:

```
{"message": "Hello user! Tip: open /docs or /redoc for documentation"}
```
