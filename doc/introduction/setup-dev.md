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
DOCKER_BUILDKIT=1 docker-compose build
```

And every time, to get the server running, just use:

```bash
docker-compose up
```

You should have a running environment.

The React application is exposed at: `http://ui.taxonomy.localhost:8091`

The API is exposed at: `http://api.taxonomy.localhost:8091`

You can also access the Neo4j Admin Console at `http://localhost:7474/browser/`

If you modify any file in the React App, the changes will be taken into account instantly.

If you modify any files related to the Python API, you need to restart the `taxonomy_api` container in Docker: `docker-compose restart taxonomy_api`

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
docker-compose run --rm taxonomy_api sample/load.py sample/test-neo4j.json
```

Add the `--reset` switch if you already have data you want to remove.

Going into the Neo4j Admin Console, you should be able to see the data.

## Without Docker

### Install Neo4j

You are required to install Neo4j in your system.

[Neo4j Desktop](https://neo4j.com/download/) (proprietary) is an option, or get the open-source [community version](https://neo4j.com/download-center/#community).

Visit this [link](https://neo4j.com/docs/operations-manual/current/installation/) for more information.

Launch it and verify it's working by visiting the Neo4j browser: `http://localhost:7474/browser/`. In the admin UI, you should connect to `localhost:7687`.

### Install the backend in a Python Virtualenv

Go to the `backend` directory of the Taxonomy Editor.

Create a virtualenv with python:

```bash
python3 -m venv .venv
```
and activate it:

```bash
source .venv
```

Install dependencies:

```bash
source pip install -r requirements.txt
```

Start the server locally:

```bash
uvicorn editor.api:app --host 127.0.0.1 --port 8080
```

Open http://127.0.0.1:8080 in your browser to check out the API.

You will see the following:
```
{"message": "Hello user! Tip: open /docs or /redoc for documentation"}
```

### Install the npm dev server

(Note: this might not be needed if you only want to work on the backend)

You must have NodeJS and npm installed on your system. (LTS - 16.17.0, currently).
See https://nodejs.org/en/download/ and https://docs.npmjs.com/cli/v7/configuring-npm/install for further installation steps.

Go to the `taxonomy-editor-frontend/` directory of the Taxonomy Editor.

Then run:

```bash
npm install .
```

Run the server with:

```bash
REACT_APP_API_URL="http://localhost:8080/" npm start
```
(or)

```bash
export REACT_APP_API_URL="http://localhost:8080/"
npm start
```

This should automatically open the Taxonomy Editor frontend in this URL: http://localhost:8080/

### Importing some test data

To import some test data, in your Python virtualenv (don't forget to activate it), in the backend directory:

```bash
python3 sample/load.py sample/test-neo4j.json
```
Add the `--reset` switch if you already have data you want to remove.

Going into the Neo4j Admin Console, you should be able to see the data.
