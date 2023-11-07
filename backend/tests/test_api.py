import pytest


@pytest.fixture(autouse=True)
def test_setup(neo4j):
    # delete all the nodes and relations in the database
    with neo4j.session() as session:
        query = "MATCH (n) DETACH DELETE n"
        session.run(query)
        query = "DROP INDEX p_test_branch_SearchIds IF EXISTS"
        session.run(query)
        query = "DROP INDEX p_test_branch_SearchTags IF EXISTS"
        session.run(query)


def test_hello(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello user! Tip: open /docs or /redoc for documentation"}


def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json().get("ping").startswith("pong @")


def test_import_from_github(client, mocker):
    mocker.patch("editor.api.TaxonomyGraph.is_branch_unique", return_value=True)
    mocker.patch("editor.api.TaxonomyGraph.import_from_github", return_value=True)
    response = client.post(
        "/test/testing_branch/import",
        json={"description": "test_description"},
    )
    assert response.status_code == 200
    assert response.json() is True


def test_upload_taxonomy(client, mocker):
    mocker.patch("editor.api.TaxonomyGraph.is_branch_unique", return_value=True)
    mocker.patch("editor.api.TaxonomyGraph.upload_taxonomy", return_value=True)
    with open("tests/data/test.txt", "rb") as f:
        response = client.post(
            "/test_taxonomy/test_branch/upload",
            files={"file": f},
            data={"description": "test_description"},
        )
    assert response.status_code == 200
    assert response.json() is True


def test_add_taxonomy_duplicate_branch_name(client, mocker):
    mocker.patch("editor.api.TaxonomyGraph.is_branch_unique", return_value=False)
    with open("tests/data/test.txt", "rb") as f:
        response = client.post(
            "/test_taxonomy_2/test_branch/upload",
            files={"file": f},
            data={"description": "test_description"},
        )
    assert response.status_code == 409
    assert response.json() == {"detail": "branch_name: Branch name should be unique!"}


def test_add_taxonomy_invalid_branch_name(client):
    with open("tests/data/test.txt", "rb") as f:
        response = client.post(
            "/test_taxonomy/invalid-branch-name/upload",
            files={"file": f},
            data={"description": "test_description"},
        )
    assert response.status_code == 400
    assert response.json() == {"detail": "branch_name: Enter a valid branch name!"}


def test_add_taxonomy_duplicate_project_name(client, mocker):
    mocker.patch("editor.api.TaxonomyGraph.does_project_exist", return_value=True)
    with open("tests/data/test.txt", "rb") as f:
        response = client.post(
            "/test_taxonomy/test_branch/upload",
            files={"file": f},
            data={"description": "test_description"},
        )
    assert response.status_code == 409
    assert response.json() == {"detail": "Project already exists!"}


def test_delete_project(neo4j, client):
    with neo4j.session() as session:
        create_project = """
            CREATE (n:PROJECT)
            SET n.id = 'test_project'
            SET n.taxonomy_name = 'test_taxonomy_name'
            SET n.branch = 'test_branch'
            SET n.description = 'test_description'
            SET n.status = 'OPEN'
            SET n.project_name = 'p_test_taxonomy_name_test_branch_name'
            SET n.created_at = datetime()
        """

        create_project2 = """
            CREATE (n:PROJECT)
            SET n.id = 'test_project2'
            SET n.taxonomy_name = 'test_taxonomy_name2'
            SET n.branch = 'test_branch2'
            SET n.description = 'test_description2'
            SET n.status = 'OPEN'
            SET n.project_name = 'p_test_taxonomy_name_test_branch_name2'
            SET n.created_at = datetime()
        """
        session.run(create_project)
        session.run(create_project2)

        response = client.delete("/test_taxonomy_name/test_branch/delete")
        assert response.status_code == 200
        assert response.json() == {"message": "Deleted 1 projects"}

        response = client.delete("/test_taxonomy_name2/test_branch2/delete")
        assert response.status_code == 200
        assert response.json() == {"message": "Deleted 1 projects"}
