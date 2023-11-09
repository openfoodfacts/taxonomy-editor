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


@pytest.fixture
def github_mock(mocker):
    github_mock = mocker.patch("github.Github")
    github_mock.return_value.get_repo.return_value.get_branches.return_value = [mocker.Mock()]
    return github_mock


def test_hello(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello user! Tip: open /docs or /redoc for documentation"}


def test_ping(client):
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.json().get("ping").startswith("pong @")


def test_import_from_github(client, github_mock, mocker):
    # We mock the TaxonomyGraph.import_from_github method,
    # which downloads the taxonomy file from a Github URL
    mocker.patch("editor.api.TaxonomyGraph.import_from_github", return_value=True)

    response = client.post(
        "/test/testing_branch/import",
        json={"description": "test_description"},
    )

    assert response.status_code == 200
    assert response.json() is True


def test_upload_taxonomy(client, github_mock):
    with open("tests/data/test.txt", "rb") as f:
        response = client.post(
            "/test_taxonomy/test_branch/upload",
            files={"file": f},
            data={"description": "test_description"},
        )

    assert response.status_code == 200
    assert response.json() is True


def test_add_taxonomy_duplicate_branch_name(client, github_mock):
    github_mock.return_value.get_repo.return_value.get_branches.return_value[0].name = "test_branch"

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


def test_add_taxonomy_duplicate_project_name(client, github_mock):
    test_upload_taxonomy(client, github_mock)

    with open("tests/data/test.txt", "rb") as f:
        response = client.post(
            "/test_taxonomy/test_branch/upload",
            files={"file": f},
            data={"description": "test_description"},
        )

    assert response.status_code == 409
    assert response.json() == {"detail": "Project already exists!"}


def test_delete_project(client, github_mock):
    test_upload_taxonomy(client, github_mock)

    response = client.delete("/test_taxonomy/test_branch/delete")

    assert response.status_code == 200
    assert response.json() == {"message": "Deleted 1 projects"}
