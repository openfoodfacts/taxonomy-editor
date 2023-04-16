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
        SET n.branch_name = 'test_branch_name'
        SET n.description = 'test_description'
        SET n.status = 'OPEN'
        SET n.created_at = datetime()
    """
    result = session.run(create_project)
    response = client.delete("/test_taxonomy_name/test_branch_name/delete")
    assert response.status_code == 200
    # assert response.json() == {"message": ""}

    # this is temporary test, just to check if the branch and taxonomy are  created
    query = "MATCH (n:test_taxonomy_name:test_branch_name) RETURN COUNT(*)"
    result = session.run(query)
    number_of_nodes = result.value()[0]
    assert number_of_nodes == 0

    session.close()
