# This Dockerfile is used to setup an image for code linting (namely config files)
FROM node:lts

WORKDIR /code

COPY package*.json ./

RUN npm install