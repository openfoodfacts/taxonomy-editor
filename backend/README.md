# Dev Environment Setup Guide
This guide will allow you to rapidly build a ready-to-use developement environment for the Taxonomy Editor API running in Docker.

## Prerequisites
Docker is the easiest way to install the Taxonomy Editor API, play with it, and even modify the code.

Docker provides an isolated environment, very close to a Virtual Machine. This environment contains everything required to launch the API. There is no need to install any modules separately.

**Installation steps:**
- [Install Docker CE](https://docs.docker.com/install/#supported-platforms)
> If you run e.g. Debian, don't forget to add your user to the `docker` group!
- [Install Docker Compose](https://docs.docker.com/compose/install/)
- [Enable command-line completion](https://docs.docker.com/compose/completion/)


## Setup with docker-compose

Go to root directory.

Launch `docker-compose up`

## Check it!

You should be able to check it in your Docker container's URL, for example: http://127.0.0.1/ or http://192.168.99.100/ (or equivalent, using your Docker host)

You will see the following:
```
{"message": "Hello user! Tip: open /docs or /redoc for documentation"}
```
