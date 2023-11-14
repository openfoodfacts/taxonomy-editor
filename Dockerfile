FROM node:lts

WORKDIR /code

COPY package*.json ./

RUN npm install