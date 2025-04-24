import json
import os

import pytest

from sample.load import load_file
from .utils import compare_db_with_dump


@pytest.fixture(autouse=True)
async def test_setup(database_lifespan, anyio_backend):
    # delete all the nodes and relations in the database
    async with database_lifespan.session() as session:
        query = "MATCH (n) DETACH DELETE n"
        await session.run(query)
        query = "DROP INDEX p_test_branch_SearchIds IF EXISTS"
        await session.run(query)
        query = "DROP INDEX p_test_branch_SearchTagsIds IF EXISTS"
        await session.run(query)


def test_hello(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello user! Tip: open /docs or /redoc for documentation"}


def test_ping(client):
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.json().get("ping").startswith("pong @")


def _upload_taxonomy(client):
    with open("tests/data/test.txt", "rb") as f:
        response = client.post(
            "/test_taxonomy/test_branch/upload",
            files={"file": f},
            data={"description": "test_description"},
        )

    assert response.status_code == 200
    assert response.json() is True


def test_upload_taxonomy(client, update_test_results):
    _upload_taxonomy(client)
    db, expected = compare_db_with_dump("test_upload_taxonomy.json",update_test_results)
    assert db == expected


def test_add_taxonomy_invalid_branch_name(client):
    with open("tests/data/test.txt", "rb") as f:
        response = client.post(
            "/test_taxonomy/invalid-branch-name/upload",
            files={"file": f},
            data={"description": "test_description"},
        )

    assert response.status_code == 422
    assert response.json() == {"detail": "branch_name: Enter a valid branch name!"}


def test_add_taxonomy_duplicate_project_name(client):
    _upload_taxonomy(client)

    with open("tests/data/test.txt", "rb") as f:
        response = client.post(
            "/test_taxonomy/test_branch/upload",
            files={"file": f},
            data={"description": "test_description"},
        )

    assert response.status_code == 409
    assert response.json() == {"detail": "Project already exists!"}


def test_delete_project(client, update_test_results):
    _upload_taxonomy(client)

    response = client.delete("/test_taxonomy/test_branch")

    assert response.status_code == 204
    db, expected = compare_db_with_dump("test_delete_project.json", update_test_results)
    assert db == expected


def test_load_and_dump():
    """Here we are testing the tool"""
    # Path to the test data JSON file
    test_data_path = "sample/dumped-test-taxonomy.json"

    # Run load.py to import data into Neo4j database
    load_file(test_data_path)

    db, expected = compare_db_with_dump(test_data_path, update_test_results=False)
    assert db == expected