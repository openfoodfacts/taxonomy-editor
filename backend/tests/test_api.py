import pytest
from backend.editor.api import api
from falcon import testing


@pytest.fixture(autouse=True)
def test_setup(neo4j):
    # delete all the nodes and relations in the database
    query = "MATCH (n:p_test_branch:t_test:b_branch) DETACH DELETE n"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchIds IF EXISTS"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchTags IF EXISTS"
    neo4j.session().run(query)

@pytest.fixture()
def client():
    return testing.TestClient(api)

def test_hello(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello user! Tip: open /docs or /redoc for documentation"}

def delete_project_test(neo4j):
    session = neo4j.session()
    query = "MATCH (n:p_test_branch:t_test:b_branch:ENTRY) RETURN COUNT(*)"

    create_project = """
            CREATE (n:PROJECT)
            SET n.id = test_project
            SET n.taxonomy_name = testtaxonomyname
            SET n.branch_name = testbranchname
            SET n.description = testdescription
            SET n.status = OPEN
            SET n.created_at = datetime()
        """
    result = session.run(create_project)
    import pdb; pdb.set_trace();
    stimulate_api_result = client.simulate_get("/testtaxonomyname/testbranchname/delete")
    assert stimulate_api_result.status_code == 200
    assert stimulate_api_result.json == {}
