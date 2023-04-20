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
        SET n.project_name = 'p_test_taxonomy_name_test_branch_name'
        SET n.created_at = datetime()
    """
    result = session.run(create_project)

    # check if the record was created
    query = """
        MATCH (n:PROJECT {id: 'test_project'})
        RETURN n.id, n.taxonomy_name, n.branch_name, n.description, n.status, n.created_at, n.project_name
    """
    result = session.run(query)
    record = result.single()

    assert record['n.id'] == 'test_project'
    assert record['n.taxonomy_name'] == 'test_taxonomy_name'
    assert record['n.branch_name'] == 'test_branch_name'
    assert record['n.description'] == 'test_description'
    assert record['n.status'] == 'OPEN'
    assert record['n.created_at'] is not None
    assert record['n.project_name'] == "p_test_taxonomy_name_test_branch_name"
    # check ends here

    response = client.delete("/test_taxonomy_name/test_branch_name/delete")
    assert response.status_code == 200
    assert response.json() == {"message": "Deleted 1 projects"}
    session.close()
