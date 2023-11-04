# Setup a dev environment

- [frontend doc](../../taxonomy-editor-frontend/README.md)
- [backend doc](../../backend/README.md)

## Using Docker

Docker is the easiest way to install the Taxonomy Editor, play with it, and even modify the code.

Docker provides an isolated environment, very close to a Virtual Machine. This environment contains everything required to launch the Taxonomy Editor. There is no need to install any modules separately.

### Prerequisites

- [Install Docker CE](https://docs.docker.com/install/#supported-platforms)
  > If you run e.g. Debian, don't forget to add your user to the `docker` group!
- [Install Docker Compose](https://docs.docker.com/compose/install/)
- [Enable command-line completion](https://docs.docker.com/compose/completion/)

### Setup

The docker-compose for Taxonomy Editor is designed in such a way that all development servers can be built rapidly.

After first checkout, or on requirements or important element changes, run the following commands in the root directory:

```bash
make build
```

And every time, to get the server running, just use:

```bash
make up
```

You should have a running environment.

The React application is exposed at: `http://ui.taxonomy.localhost:8091`

The API is exposed at: `http://api.taxonomy.localhost:8091`

You can also access the Neo4j Admin Console at `http://localhost:7474/browser/`

If you modify any file in the React App, the changes will be taken into account instantly.
However, this feature is not compatible with Windows systems. In order to use live reload on a Windows machine, you will need to install and use [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install). This will allow you to run the development server in a Linux environment, and the live reload feature will work as expected.

If you modify any files related to the Python API, you need to restart the `taxonomy_api` container in Docker: `docker compose restart taxonomy_api`

You can modify the `.env` file to fit your needs, but you should not commit any changes that are not defaults to the project.
Notably, if you use a `uid` which is not 1000, you should personalize the `USER_UID` variable.

A smarter way to customize things, is to use [direnv](https://direnv.net/) with a `.envrc` file, or to simply have a script to source (see [the `.` command](https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html#Bourne-Shell-Builtins)) to load environment variables (they have priority above `.env`).

### Creating Pull Requests with the Taxonomy Editor

If you are using docker, the [.env](https://github.com/openfoodfacts/taxonomy-editor/blob/main/.env) file must be updated in order to use the feature. If you'd like to see it in action in development mode, do the following steps:

- Make sure a fork of openfoodfacts-server repository is created in your Github account.
- Update the `access_token` variable in `.env` with your [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).
- Update the `repo_uri` variable in `.env` with your Github for uri: (username/repository_name)

That's it! Now, you'll be able to view any created PR's in your fork of Taxonomy Editor.

### Importing some test data

```bash
docker compose run --rm taxonomy_api sample/load.py sample/test-neo4j.json
```

Add the `--reset` switch if you already have data you want to remove.

Going into the Neo4j Admin Console, you should be able to see the data.

## Local Development without Docker

Even if you want to run the frontend and backend servers without Docker, it is recommended you still use Docker for Neo4J.

### Install local dependencies

Before running the local dependencies installation script, you need to have the following installed on you system:

- NodeJS and npm (LTS - 16.17.0, currently)
  See https://nodejs.org/en/download/ and https://docs.npmjs.com/cli/v7/configuring-npm/install for further installation steps.
  We recommend using [nvm](https://github.com/nvm-sh/nvm) to handle several NodeJS versions.

- Python 3.11
  See https://www.python.org/downloads/ for further installation steps.
  We recommend using [pyenv](https://github.com/pyenv/pyenv) to handle several Python versions.

- Poetry
  See https://python-poetry.org/docs/#installation for further installation steps.

Once these are installed, run `make install`.

### Install Neo4j (optional)

If you do not have Docker installed, you are required to install Neo4j in your system.

[Neo4j Desktop](https://neo4j.com/download/) (proprietary) is an option, or get the open-source [community version](https://neo4j.com/download-center/#community).

Visit this [link](https://neo4j.com/docs/operations-manual/current/installation/) for more information.

Launch it and verify it's working by visiting the Neo4j browser: `http://localhost:7474/browser/`. In the admin UI, you should connect to `localhost:7687`.

### Running the local environment

In 3 separate terminals, run

```bash
make local-frontend
```

```bash
make local-backend
```

and if you are using Docker for Neo4J

```bash
make databases
```

You will see:

- the Taxnonomy Editor Frontend at http://localhost:8080/
- the API docs at http://127.0.0.1:8080/docs
- the Neo4j browser at http://localhost:7474/browser/

You are able to add local test data with

```bash
make add-local-test-data
```

Going into the Neo4j browser, you should be able to see the data.
