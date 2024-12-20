import json
import os

import pytest

from sample.dump import dump_db
from sample.load import load_file


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


def test_upload_taxonomy(client):
    with open("tests/data/test.txt", "rb") as f:
        response = client.post(
            "/test_taxonomy/test_branch/upload",
            files={"file": f},
            data={"description": "test_description"},
        )

    assert response.status_code == 200
    assert response.json() is True


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
    test_upload_taxonomy(client)

    with open("tests/data/test.txt", "rb") as f:
        response = client.post(
            "/test_taxonomy/test_branch/upload",
            files={"file": f},
            data={"description": "test_description"},
        )

    assert response.status_code == 409
    assert response.json() == {"detail": "Project already exists!"}


def test_delete_project(client):
    test_upload_taxonomy(client)

    response = client.delete("/test_taxonomy/test_branch")

    assert response.status_code == 204


def test_load_and_dump():
    # Path to the test data JSON file
    test_data_path = "sample/dumped-test-taxonomy.json"

    # Run load.py to import data into Neo4j database
    load_file(test_data_path)

    # Run dump.py to dump the Neo4j database into a JSON file
    dumped_file_path = "sample/dump.json"
    dump_db(dumped_file_path)

    try:
        # Read the original and dumped JSON files
        with open(test_data_path, "r") as original_file:
            original_data = json.load(original_file)

        with open(dumped_file_path, "r") as dumped_file:
            dumped_data = json.load(dumped_file)

        # Label order does not matter: make it a set
        for node in original_data["nodes"]:
            node["labels"] = set(node["labels"])
        for node in dumped_data["nodes"]:
            node["labels"] = set(node["labels"])

        # Relation order does not matter: sort relations
        original_data["relations"].sort(key=json.dumps)
        dumped_data["relations"].sort(key=json.dumps)

        # Perform assertions to compare the JSON contents
        assert original_data == dumped_data

    finally:
        # Clean up: remove the dumped file
        os.remove(dumped_file_path)
