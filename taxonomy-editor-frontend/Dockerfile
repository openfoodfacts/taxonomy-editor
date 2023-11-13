# syntax = docker/dockerfile:1.2
# Base user uid / gid keep 1000 on prod, align with your user on dev
ARG USER_UID=1000
ARG USER_GID=1000


# builder is the node service, only used to build project in prod
FROM node:lts as builder
ARG USER_UID
ARG USER_GID
RUN usermod --uid $USER_UID node && \
    groupmod --gid $USER_GID node && \
    mkdir -p /opt/taxonomy-editor/node_modules && \
    mkdir -p /opt/taxonomy-editor/src && \
    mkdir -p /opt/taxonomy-editor/public && \
    mkdir -p /home/node/.npm && \
    chown node:node -R /opt/taxonomy-editor/ && \
    chown node:node -R /home/node/.npm
# tricky but we can't set uid and gid from variables with RUN --mount
# so we ensure permissions while we are root
RUN --mount=type=cache,id=taxonomy-editor-npm-cache,target=/home/node/.npm,mode=0777 \
  chown -R node:node /home/node/.npm
COPY --chown=node:node package*.json /opt/taxonomy-editor/
WORKDIR /opt/taxonomy-editor
USER node
# install dependencies
RUN --mount=type=cache,id=taxonomy-editor-npm-cache,target=/home/node/.npm,mode=0777 \
  npm install
# add local binaries to path
ENV PATH /opt/taxonomy-editor/node_modules/.bin:$PATH

# copy files
COPY --chown=node:node src /opt/taxonomy-editor/src
COPY --chown=node:node public /opt/taxonomy-editor/public
COPY --chown=node:node tsconfig.json /opt/taxonomy-editor/tsconfig.json
COPY --chown=node:node webpack.config.js /opt/taxonomy-editor/webpack.config.js
# build for production
# no need of a public url, we are at the root
RUN npm run build

# ngixn
FROM nginx:stable
WORKDIR /opt/taxonomy-editor
ARG USER_UID
ARG USER_GID
RUN usermod -u $USER_UID www-data && \
    groupmod --gid $USER_GID www-data
COPY --from=builder /opt/taxonomy-editor/build/ /opt/taxonomy-editor/build/