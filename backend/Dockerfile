FROM python:3.8
WORKDIR /code
COPY backend/requirements.txt /code/requirements.txt
COPY backend/editor /code/editor
COPY parser  /parser
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# this is purely cosmetic
RUN     ln -s /parser/openfoodfacts_taxonomy_parser /code/openfoodfacts_taxonomy_parser
CMD ["uvicorn", "editor.api:app", "--host", "0.0.0.0", "--port", "80"]