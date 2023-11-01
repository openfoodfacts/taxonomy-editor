# Developing with Neo4j

We provide a simple docker compose for neo4j to have it available on your localhost.

> **Note**: this may be a temporary setting, as later on we may have all running in docker.

## Launching the database

To start the database, simply type `docker compose up neo4j` at root of project.

The neo4j database will be available at `localhost:7687` using bolt protocol.

Moreover you can access an admin tool at http://localhost:7474/.

To stop the database, simply use _Ctrl+C_ in the console where neo4j is running, or type `docker compose stop` in another terminal.

If you want to **destroy** neo4j data, simply use `docker compose rm -sf neo4j` and then `docker volume rm taxonomy-editor_neo4j-data`[^vol_name]

[^vol_name]: (it may have another name, look at what `docker volume list|grep neo4j-data`) gives you.

## Importing data into Neo4J database

### Import sample data

We have a `backend/sample/test-neo4j.json` file to load sample data in the database for developers.

To load it:

- ensure your neo4j database is launched:
  ```bash
  docker compose up -d neo4j
  ```
- create you local env if you do not have one yet:
  ```bash
  python3 -m venv .venv
  ```
- activate your local env, if needed:
  ```bash
  . .venv/bin/activate
  ```
- if needed, install neo4j driver:
  ```bash
  pip install neo4j
  ```
- finally load the data:

  ```bash
  cd backend/sample
  python3 load.py --reset test-neo4j.json
  ```

  note that if you want to see more options, you can use `--help`

- enjoy it in the neo4j browser at http://localhost:7474
  (Hint: After connecting the database, on the left click on the "\*" node types to visualize a beautiful graph of the loaded taxonomy)

### From a generic file

Note that if you want to import some other data, (eg for a specific test of Neo4J capabilities),
the file needs to be placed inside the `neo4j/import` folder.

Then see [neo4j documentation on importing data](https://neo4j.com/docs/operations-manual/current/docker/operations/#docker-neo4jlabs-pluginsneo4j.com) but you can run the simpler command:

```
docker compose exec neo4j neo4j-admin import ...
```

> **Note**: it haven't been tested so far, and some tweaks might be necessary.

## Use it locally

If you are using a local python environment, the database will be accessible at `localhost:7687`

## Use it in another docker service

If you run another docker service and want to access neo4j, it will be accessible at `neo4j:7687`
provided your container runs in the same network (should default to `taxonomy-editor_default`)
