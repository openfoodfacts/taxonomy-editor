import pytest
import taxonomy_parser as parser
import re


def test_normalized_filename():
    x = parser.Parser()
    normalizer = x.normalized_filename
    name = normalizer("test")
    assert name == "test.txt"
    name = normalizer("test.txt")
    assert name == "test.txt"
    name = normalizer("t")
    assert name == "t.txt"

def test_fileiter():
    x=parser.Parser()
    file=x.file_iter("test.txt")
    counter=0
    language_code_prefix = re.compile('[a-zA-Z][a-zA-Z]:')
    for _,line in file:
        counter+=1
        assert line == '' or line[0]=="#" or ":" in line
        if counter==27:
            assert line == "carbon_footprint_fr_foodges_value:fr:10"
    assert counter == 37+1

def test_normalizing():
    x=parser.Parser()
    text="Numéro #1, n°1 des ¾ des Français*"
    text=x.normalizing(text,"fr")
    assert text == "numero-1-n-1-des-des-francais"
    text="Randôm Languäge wìth àccénts"
    text=x.normalizing(text,"fr")
    assert text == "random-language-with-accents"

def test_create_nodes():
    x=parser.Parser()

    #first delete all the nodes and relations in the database
    query="MATCH (n) DETACH DELETE n"
    x.session.run(query)

    x.create_nodes("test")

    # total number of nodes
    query="MATCH (n) RETURN COUNT(*)"
    result = x.session.run(query)
    number_of_nodes = result.value()[0]
    assert number_of_nodes == 12

    # header correctly added
    query="MATCH (n) WHERE n.id = '__header__' RETURN n.value"
    result = x.session.run(query)
    header = result.value()[0]
    assert header == ['test-taxonomy']

    # comment / preceding lines correctly added
    query="MATCH (n) WHERE size(n.preceding_lines)>0 RETURN n.id"
    result = x.session.run(query)
    nodes = result.values()
    number_of_nodes = len(nodes)
    assert number_of_nodes == 1
    assert nodes[0][0] == 'en:meat'

def test_create_child_link():
    x=parser.Parser()
    x.create_child_link() # nodes added in the precedent test

    # correct number of links
    query="MATCH ()-[r]->() RETURN COUNT(r)"
    result = x.session.run(query)
    number_of_links = result.value()[0]
    assert number_of_links == 6

    # correct number of links for each child node
    query="MATCH (n)-[r]->() RETURN n.id,n.parents,count(r)"
    results = x.session.run(query)
    for result in results:
        assert len(result['n.parents']) == result['count(r)']
    assert number_of_links == 6



if __name__ == "__main__":
    pytest.main()