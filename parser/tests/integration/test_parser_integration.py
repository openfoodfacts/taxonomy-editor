import pytest
import pathlib
from openfoodfacts_taxonomy_parser import parser

# taxonomy in text format : test.txt
TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test")

@pytest.fixture(autouse=True)
def test_setup():
    # delete all the nodes and relations in the database
    query="MATCH (n) DETACH DELETE n"
    parser.Parser().session.run(query)

def test_calling():
    test_parser = parser.Parser()
    session = test_parser.session

    #Create node test
    test_parser.create_nodes(TEST_TAXONOMY_TXT)

    # total number of nodes
    query="MATCH (n) RETURN COUNT(*)"
    result = session.run(query)
    number_of_nodes = result.value()[0]
    assert number_of_nodes == 13

    # header correctly added
    query="MATCH (n) WHERE n.id = '__header__' RETURN n.preceding_lines"
    result = session.run(query)
    header = result.value()[0]
    assert header == ['# test taxonomy']


    # synonyms correctly added
    query="MATCH (n:SYNONYMS) RETURN n ORDER BY n.src_position"
    results = session.run(query)
    expected_synonyms = [
        { "id" : "synonyms:0",
        "tags_en" : ["passion fruit", "passionfruit"],
        "tags_ids_en" : ["passion-fruit", "passionfruit"],
        "preceding_lines" : [],
        "src_position" : 5 },
        { "id" : "synonyms:1",
        "tags_fr" : ["fruit de la passion", "maracuja", "passion"],
        "tags_ids_fr" : ["fruit-passion", "maracuja", "passion"],
        "preceding_lines" : [""],
        "src_position" : 7 }
    ]
    for i, result in enumerate(results):
        node = result.value()
        for key in expected_synonyms[i]:
            assert node[key] == expected_synonyms[i][key]


    # stopwords correctly added
    query="MATCH (n:STOPWORDS) RETURN n"
    results = session.run(query)
    expected_stopwords = {
        "id" : "stopwords:0",
        "tags_fr" : ["aux", "au", "de", "le", "du", "la", "a", "et"],
        "preceding_lines" : []
    }
    for result in results:
        node = result.value()
        for key in expected_stopwords:
            assert node[key] == expected_stopwords[key]


    # entries correctly added
    # check for two of them
    query = """
        MATCH (n:ENTRY) 
        WHERE n.id='en:banana-yogurts' 
        OR n.id='en:meat'
        RETURN n
        ORDER BY n.src_position
    """
    results = session.run(query)
    expected_entries = [
        { "tags_en" : ["banana yogurts"],
        "tags_ids_en" : ["banana-yogurts"],
        "tags_fr" : ["yaourts à la banane"],
        "tags_ids_fr" : ["yaourts-banane"],
        "preceding_lines" : [], },
        {"tags_en" : ["meat"],
        "tags_ids_en" : ["meat"],
        "preceding_lines" : ['# meat',''],
        "prop_vegan_en" : "no",
        "prop_carbon_footprint_fr_foodges_value_fr" : "10" }
    ]
    for i, result in enumerate(results):
        node = result.value()
        for key in expected_entries[i]:
            assert node[key] == expected_entries[i][key]


    #Child link test
    test_parser.create_child_link() # nodes already added
    query="MATCH (c)-[:is_child_of]->(p) RETURN c.id, p.id"
    results = session.run(query)
    created_pairs = results.values()

    # correct number of links
    number_of_links = len(created_pairs)
    assert number_of_links == 6

    # correctly linked
    expected_pairs = [
            ['en:banana-yogurts', 'en:yogurts'],
            ['en:passion-fruit-yogurts', 'en:yogurts'],
            ['fr:yaourts-fruit-passion-alleges', 'en:passion-fruit-yogurts'],
            ['en:fake-meat', 'en:meat'],
            ['en:fake-duck-meat', 'en:fake-meat'],
            ['en:fake-duck-meat', 'en:fake-stuff']
    ]
    for pair in created_pairs:
        assert pair in expected_pairs
    

    # Order link test
    test_parser.create_previous_link()
    query="MATCH (n)-[:is_before]->(p) RETURN n.id, p.id "
    results = session.run(query)
    created_pairs = results.values()

    # correct number of links
    number_of_links = len(created_pairs)
    assert number_of_links == 12

    # correctly linked
    expected_pairs = [
        ['__header__', 'stopwords:0'],
        ['stopwords:0', 'synonyms:0'],
        ['synonyms:0', 'synonyms:1'],
        ['synonyms:1', 'en:yogurts'],
        ['en:yogurts', 'en:banana-yogurts'],
        ['en:banana-yogurts', 'en:passion-fruit-yogurts'],
        ['en:passion-fruit-yogurts', 'fr:yaourts-fruit-passion-alleges'],
        ['fr:yaourts-fruit-passion-alleges', 'en:meat'],
        ['en:meat', 'en:fake-meat'],
        ['en:fake-meat', 'en:fake-stuff'],
        ['en:fake-stuff', 'en:fake-duck-meat'],
        ['en:fake-duck-meat', '__footer__']
    ]
    for pair in created_pairs:
        assert pair in expected_pairs
