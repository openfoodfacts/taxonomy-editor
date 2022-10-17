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


### Importing some test data

```bash
docker-compose run --rm taxonomy_api sample/load.py sample/test-neo4j.json
```

Add the `--reset` switch if you already have data you want to remove.

Going into the neo4j admin console you should be able to see the data.


## Without docker

### Install neo4j

You should install neo4j on your system.
Maybe neo4J Desktop (proprietary) is an option : https://neo4j.com/download/ or get the community open source server : https://neo4j.com/download-center/#community
See https://neo4j.com/docs/operations-manual/current/installation/

Launch it and verify it's working by visiting: http://localhost:7474/browser/
in the admin ui, you should connect to `localhost:7687`.

### Install the backend in a python virtualenv

Go to backend directory backend
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
# ROBOTOFF_URL=http://api:5500 # connect to Robotoff running in separate docker-compose deployment
```

Start the server locally

```bash
uvicorn editor.api:app --host 127.0.0.1 --port 8080
```

Open http://127.0.0.1:8080 in your browser, you should see a simple message.

### Install the npm dev server

(note: this might not be needed if you only want to work on the backend)

You must have nodeJS and npm installed on your system. (LTS - 16.17.0, currently)
See https://nodejs.org/en/download/ and https://docs.npmjs.com/cli/v7/configuring-npm/install

Go to `taxonomy-editor-frontend/`

Then run:

```bash
npm install .
```

Then run the server with:

```bash
REACT_APP_API_URL="http://localhost:8080/" npm start
```
or 

```bash
export REACT_APP_API_URL="http://localhost:8080/"
npm start
```

This should open http://localhost:8080/


### Importing some test data

To import some test data, in your python virtualenv (don't forget to activate it), in the backend directory:

```bash
python3 sample/load.py sample/test-neo4j.json
```
Add the `--reset` switch if you already have data you want to remove.

Going into the neo4j admin console you should be able to see the data.
