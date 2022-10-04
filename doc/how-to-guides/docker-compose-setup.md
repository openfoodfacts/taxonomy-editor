# Docker compose setup

The docker compose setup is a simple setup. A bit of subtlety comes in nginx.

We have:
- neo4j database
- api service - a fastapi app (taxonomy_api)
- nginx as the frontend (taxonomy_frontend)
  - it routes requests to `api.xxx` which is the FastAPI app
  - it routes requests to ui.xxxx to:
    - the React dev server in development
    - or serves the static files present in the image (built during docker build phase)
- in dev (dev.yml), we also run a taxonomy_node service which is the react development server

For nginx, the routing difference between dev and prod,
is managed by adding a suffix to production virtual server
through the `PROD_UI_SUFFIX` env variable (see ``conf/nginx.conf``)

For dev, it's important to have the same UID/GID for users in docker and for the developer,
in order to avoid permissions problems.
This is accomplished thanks to `USER_UID` and `USER_GID` parameters.