# Setup a dev environment

## Using docker

The docker-compose for Taxonomy Editor is designed in such a way that all development servers can be built rapidly.

After first checkout, or on requirements or important element changes, run:

```bash
DOCKER_BUILDKIT=1 docker-compose build
```

And every time, to get the server running, just use:

```bash
docker-compose up
```

You should have a running environment.

The react application is exposed at: `http://ui.taxonomy.localhost:8091`

The api is exposed at: `http://api.taxonomy.localhost:8091`

You can also access the neo4j admin ui at http://localhost:7474/browser/

If you modify any file in the React App, the changes will be taken into account instantly.

If you modify the python code you need to restart the taxonomy_api: `docker-compose restart taxonomy_api`

You can modify the `.env` file to fit your needs, but you should not commit any changes that are not defaults to the project.
Notably, if you user `uid` is not 1000, you should personalize the `USER_UID` variable.

A smarter way to customize things it to use [direnv](https://direnv.net/) with a `.envrc` file, or to simply have a script to source (see [the `.` command](https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html#Bourne-Shell-Builtins)) to load environment variables (they have priority above `.env`).
