import pytest

#importing parser
import os,sys
script_dir = os.path.dirname( '__file__' )
mymodule_dir = os.path.join( script_dir, '..' , '..', 'openfoodfacts_taxonomy_parser')
sys.path.append( mymodule_dir )
import parser

@pytest.fixture
def new_session():
    x = parser.Parser()
    # delete all the nodes and relations in the database
    query="MATCH (n) DETACH DELETE n"
    x.session.run(query)
    return x


def test_calling(new_session):
    x=new_session

    #Create node test
    x.create_nodes("test")

    # total number of nodes
    query="MATCH (n) RETURN COUNT(*)"
    result = x.session.run(query)
    number_of_nodes = result.value()[0]
    assert number_of_nodes == 13

    # header correctly added
    query="MATCH (n) WHERE n.id = '__header__' RETURN n.preceding_lines"
    result = x.session.run(query)
    header = result.value()[0]
    assert header == ['# test-taxonomy']

    # comment / preceding lines correctly added
    query="MATCH (n) WHERE size(n.preceding_lines)>0 RETURN n.id,n.preceding_lines"
    result = x.session.run(query)
    nodes = result.values()
    number_of_nodes = len(nodes)
    assert number_of_nodes == 1
    assert nodes[0][0] == 'en:meat'
    assert nodes[0][1] == ['# meat','']



    #Child link test
    x.create_child_link() # nodes already added
    query="MATCH (c)-[:is_child_of]->(p) RETURN c.id, p.id"
    results = x.session.run(query)
    created_pairs = results.values()

    # correct number of links
    number_of_links = len(created_pairs)
    assert number_of_links == 6

    # correctly linked
    expected_pairs = [
            ['en:banana-yogurts', 'en:yogurts'],
            ['en:passion-fruit-yogurts', 'en:yogurts'],
            ['fr:yaourts-au-fruit-de-la-passion-alleges', 'en:passion-fruit-yogurts'],
            ['en:fake-meat', 'en:meat'],
            ['en:fake-duck-meat', 'en:fake-meat'],
            ['en:fake-duck-meat', 'en:fake-stuff']
    ]
    for pair in created_pairs:
        assert pair in expected_pairs


if __name__ == "__main__":
    pytest.main()