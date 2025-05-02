import pytest

from .test_utils import compare_db_with_dump, compare_taxonomy, match_taxonomy


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


def _upload_taxonomy(client, path="tests/data/test.txt"):
    with open(path, "rb") as f:
        response = client.post(
            "/test_taxonomy/test_branch/upload",
            files={"file": f},
            data={"description": "test_description"},
        )

    assert response.status_code == 200
    assert response.json() is True


def test_upload_taxonomy(client, update_test_results):
    _upload_taxonomy(client)
    compare_db_with_dump("test_upload_taxonomy.json", update_test_results)


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
    compare_db_with_dump("test_delete_project.json", update_test_results)


def test_delete_node_and_export(client, update_test_results):
    _upload_taxonomy(client)

    response = client.delete("/test_taxonomy/test_branch/nodes/en:banana-yogurts")
    assert response.status_code == 200

    # export
    response = client.get("/test_taxonomy/test_branch/downloadexport")
    content = response.content.decode("utf-8")
    compare_taxonomy(
        content, "tests/data/test.txt", "test_delete_node_and_export.diff", update_test_results
    )


def test_add_and_delete_node_and_export(client):
    """
    A created then deleted node should not be exported

    Related to https://github.com/openfoodfacts/taxonomy-editor/issues/561
    """
    _upload_taxonomy(client)

    # add a node
    response = client.post(
        "/test_taxonomy/test_branch/entry",
        json={"name": "Supa Yogurts", "main_language_code": "en"},
    )
    assert response.status_code == 201
    # remove it
    response = client.delete("/test_taxonomy/test_branch/nodes/en:supa-yogurts")
    assert response.status_code == 200

    # export
    response = client.get("/test_taxonomy/test_branch/downloadexport")
    content = response.content.decode("utf-8")
    match_taxonomy(content, "tests/data/test.txt")
