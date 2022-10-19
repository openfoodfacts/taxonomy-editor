# syntax = docker/dockerfile:1.2
# Base user uid / gid keep 1000 on prod, align with your user on dev
ARG USER_UID=1000
ARG USER_GID=1000

FROM python:3.8

ARG USER_UID
ARG USER_GID

WORKDIR /code
RUN groupadd -g $USER_GID off && \
    useradd -u $USER_UID -g off -m off && \ 
    mkdir -p /home/off && \ 
    chown off:off -R /code /home/off

COPY ./requirements.txt /code/requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt
RUN --mount=type=cache,id=pip-cache,target=/root/.cache/pip \
    pip3 install --upgrade -r /code/requirements.txt

USER off:off
COPY --chown=off:off ./editor /code/editor

CMD ["uvicorn", "editor.api:app", "--host", "0.0.0.0", "--port", "80"]