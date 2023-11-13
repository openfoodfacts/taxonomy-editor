# syntax = docker/dockerfile:1.2
# Base user uid / gid keep 1000 on prod, align with your user on dev
ARG USER_UID=1000
ARG USER_GID=1000
ARG DEVELOPMENT=false

FROM python:3.11-buster as builder

ARG DEVELOPMENT
RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /code

COPY backend/pyproject.toml backend/poetry.lock ./
COPY parser /parser

RUN if [ "$DEVELOPMENT" = "false" ] ; then \
    poetry install --without dev --no-root ; \
    else \
    poetry install --no-root ; \
    fi && rm -rf $POETRY_CACHE_DIR


# The runtime image, used to just run the code provided its virtual environment
FROM python:3.11-slim-buster as runtime

ARG USER_UID
ARG USER_GID

WORKDIR /code

RUN groupadd -g $USER_GID off && \
    useradd -u $USER_UID -g off -m off && \
    mkdir -p /home/off && \
    chown off:off -R /code /home/off

ENV VIRTUAL_ENV=/code/.venv \
    PATH="/code/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY backend/editor /code/editor
COPY parser /parser

USER off:off
COPY --chown=off:off ./backend/editor /code/editor

CMD ["uvicorn", "editor.api:app", "--host", "0.0.0.0", "--port", "80"]