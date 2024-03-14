import json

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from editor.api import app as editor_app


# From https://fastapi.tiangolo.com/advanced/generate-clients/
def generate_openapi_spec(app: FastAPI):
    with open("openapi/openapi.json", "w") as f:
        json.dump(
            get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                routes=app.routes,
            ),
            f,
        )


if __name__ == "__main__":
    generate_openapi_spec(editor_app)
