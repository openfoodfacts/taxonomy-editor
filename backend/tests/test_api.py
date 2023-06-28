import pytest


@pytest.fixture(autouse=True)
def test_setup(neo4j):
    # delete all the nodes and relations in the database
    query = "MATCH (n) DETACH DELETE n"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchIds IF EXISTS"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchTags IF EXISTS"
    neo4j.session().run(query)


def test_hello(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello user! Tip: open /docs or /redoc for documentation"}


def test_delete_project(neo4j, client):
    session = neo4j.session()
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
    session.close()
