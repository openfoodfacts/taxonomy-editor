import logging
import pathlib
import textwrap

import pytest

from openfoodfacts_taxonomy_parser import parser

# taxonomy in text format : test.txt
TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test.txt")


@pytest.fixture(autouse=True)
def test_setup(neo4j):
    # delete all the nodes and relations in the database
    query = "MATCH (n:p_test_branch:t_test:b_branch) DETACH DELETE n"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchIds IF EXISTS"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchTags IF EXISTS"
    neo4j.session().run(query)


def test_calling(neo4j):
    session = neo4j.session()
    test_parser = parser.Parser(session)

    # Create node test
    test_parser.create_nodes(TEST_TAXONOMY_TXT, "p_test_branch:t_test:b_branch")

    # total number of nodes
    query = "MATCH (n:p_test_branch:t_test:b_branch) RETURN COUNT(*)"
    result = session.run(query)
    number_of_nodes = result.value()[0]
    assert number_of_nodes == 13

    # header correctly added
    query = (
        "MATCH (n:p_test_branch:t_test:b_branch) WHERE n.id = '__header__' RETURN n.preceding_lines"
    )
    result = session.run(query)
    header = result.value()[0]
    assert header == ["# test taxonomy"]

    # synonyms correctly added
    query = "MATCH (n:p_test_branch:t_test:b_branch:SYNONYMS) RETURN n ORDER BY n.src_position"
    results = session.run(query)
    expected_synonyms = [
        {
            "id": "synonyms:0",
            "tags_en": ["passion fruit", "passionfruit"],
            "tags_ids_en": ["passion-fruit", "passionfruit"],
            "preceding_lines": [],
            "src_position": 5,
        },
        {
            "id": "synonyms:1",
            "tags_fr": ["fruit de la passion", "maracuja", "passion"],
            "tags_ids_fr": ["fruit-passion", "maracuja", "passion"],
            "preceding_lines": [""],
            "src_position": 7,
        },
    ]
    for i, result in enumerate(results):
        node = result.value()
        for key in expected_synonyms[i]:
            assert node[key] == expected_synonyms[i][key]

    # stopwords correctly added
    query = "MATCH (n:p_test_branch:t_test:b_branch:STOPWORDS) RETURN n"
    results = session.run(query)
    expected_stopwords = {
        "id": "stopwords:0",
        "tags_fr": ["aux", "au", "de", "le", "du", "la", "a", "et"],
        "preceding_lines": [],
    }
    for result in results:
        node = result.value()
        for key in expected_stopwords:
            assert node[key] == expected_stopwords[key]

    # entries correctly added
    # check for two of them
    query = """
        MATCH (n:p_test_branch:t_test:b_branch:ENTRY)
        WHERE n.id='en:banana-yogurts'
        OR n.id='en:meat'
        RETURN n
        ORDER BY n.src_position
    """
    results = session.run(query)
    expected_entries = [
        {
            "tags_en": ["banana yogurts"],
            "tags_ids_en": ["banana-yogurts"],
            "tags_fr": ["yaourts à la banane"],
            "tags_ids_fr": ["yaourts-banane"],
            "preceding_lines": [],
        },
        {
            "tags_en": ["meat"],
            "tags_ids_en": ["meat"],
            "preceding_lines": ["# meat", ""],
            "prop_vegan_en": "no",
            "prop_carbon_footprint_fr_foodges_value_fr": "10",
        },
    ]
    for i, result in enumerate(results):
        node = result.value()
        for key in expected_entries[i]:
            assert node[key] == expected_entries[i][key]

    # Child link test
    test_parser.create_child_link("p_test_branch:t_test:b_branch")  # nodes already added
    query = """
        MATCH (c:p_test_branch:t_test:b_branch)-[:is_child_of]->(p:p_test_branch:t_test:b_branch)
        RETURN c.id, p.id
    """
    results = session.run(query)
    created_pairs = results.values()

    # correct number of links
    number_of_links = len(created_pairs)
    assert number_of_links == 6

    # correctly linked
    expected_pairs = [
        ["en:banana-yogurts", "en:yogurts"],
        ["en:passion-fruit-yogurts", "en:yogurts"],
        ["fr:yaourts-fruit-passion-alleges", "en:passion-fruit-yogurts"],
        ["en:fake-meat", "en:meat"],
        ["en:fake-duck-meat", "en:fake-meat"],
        ["en:fake-duck-meat", "en:fake-stuff"],
    ]
    for pair in created_pairs:
        assert pair in expected_pairs

    # Order link test
    test_parser.create_previous_link("p_test_branch:t_test:b_branch")
    query = """
        MATCH (n:p_test_branch:t_test:b_branch)-[:is_before]->(p:p_test_branch:t_test:b_branch)
        RETURN n.id, p.id
    """
    results = session.run(query)
    created_pairs = results.values()

    # correct number of links
    number_of_links = len(created_pairs)
    assert number_of_links == 12

    # correctly linked
    expected_pairs = [
        ["__header__", "stopwords:0"],
        ["stopwords:0", "synonyms:0"],
        ["synonyms:0", "synonyms:1"],
        ["synonyms:1", "en:yogurts"],
        ["en:yogurts", "en:banana-yogurts"],
        ["en:banana-yogurts", "en:passion-fruit-yogurts"],
        ["en:passion-fruit-yogurts", "fr:yaourts-fruit-passion-alleges"],
        ["fr:yaourts-fruit-passion-alleges", "en:meat"],
        ["en:meat", "en:fake-meat"],
        ["en:fake-meat", "en:fake-stuff"],
        ["en:fake-stuff", "en:fake-duck-meat"],
        ["en:fake-duck-meat", "__footer__"],
    ]
    for pair in created_pairs:
        assert pair in expected_pairs
    session.close()


def test_error_log(neo4j, tmp_path, caplog):
    # error entries with same id
    session = neo4j.session()
    test_parser = parser.Parser(session)

    taxonomy_txt = textwrap.dedent("""
    # a fake taxonomy
    stopwords:fr: aux,au,de,le,du,la,a,et

    # meat
    en:meat

    <en:meat
    en:fake-meat

    # duplicate
    en:fake-meat
    """)
    taxonomy_path = tmp_path / "test.txt"
    taxonomy_path.open("w").write(taxonomy_txt)

    # parse
    with caplog.at_level(logging.ERROR):
        test_parser(str(taxonomy_path), "branch", "test")

    # only the 2 nodes imported, not the duplicate
    query = "MATCH (n:p_test_branch:t_test:b_branch:ENTRY) RETURN COUNT(*)"
    result = session.run(query)
    number_of_nodes = result.value()[0]
    assert number_of_nodes == 2
    # error logged
    assert "Entry with same id en:fake-meat already created" in caplog.text
    assert "duplicate id in file at line 12" in caplog.text
    assert "Node creation cancelled." in caplog.text
    # and present on project
    query = "MATCH (n:ERRORS) WHERE n.id = 'p_test_branch' RETURN n"
    results = session.run(query).value()
    node = results[0]
    assert len(node["errors"]) == 1
    error = node["errors"][0]
    assert "Entry with same id en:fake-meat already created" in error
    assert "duplicate id in file at line 12" in error
    assert "Node creation cancelled." in error
