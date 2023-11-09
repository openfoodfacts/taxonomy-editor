# syntax = docker/dockerfile:1.2
# Base user uid / gid keep 1000 on prod, align with your user on dev
ARG USER_UID=1000
ARG USER_GID=1000
ARG REQUIREMENTS_FILE=requirements.txt

FROM python:3.9

ARG USER_UID
ARG USER_GID
ARG REQUIREMENTS_FILE

WORKDIR /code
RUN groupadd -g $USER_GID off && \
    useradd -u $USER_UID -g off -m off && \
    mkdir -p /home/off && \
    chown off:off -R /code /home/off

COPY backend/requirements*.txt /code/
COPY backend/editor /code/editor
COPY parser  /parser

RUN pip3 install --no-cache-dir --upgrade -r /code/$REQUIREMENTS_FILE
# this is purely cosmetic
RUN     ln -s /parser/openfoodfacts_taxonomy_parser /code/openfoodfacts_taxonomy_parser
RUN --mount=type=cache,id=pip-cache,target=/root/.cache/pip \
    pip3 install --upgrade -r /code/requirements.txt

USER off:off
COPY --chown=off:off ./backend/editor /code/editor
COPY --chown=off:off ./backend/sample /code/sample
RUN find /code/sample -type f -name '*.py' -exec chmod +x {} \;

CMD ["uvicorn", "editor.api:app", "--host", "0.0.0.0", "--port", "80"]
