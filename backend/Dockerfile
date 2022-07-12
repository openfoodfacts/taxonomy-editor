FROM python:3.8
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./editor /code/editor
CMD ["uvicorn", "editor.api:app", "--host", "0.0.0.0", "--port", "80"]