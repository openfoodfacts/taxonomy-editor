import logging
import pathlib
import textwrap

import pytest

from openfoodfacts_taxonomy_parser import parser

# taxonomy in text format : test.txt
TEST_TAXONOMY_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test.txt")
TEST_EXTERNAL_1_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test_external1.txt")
TEST_EXTERNAL_2_TXT = str(pathlib.Path(__file__).parent.parent / "data" / "test_external2.txt")


@pytest.fixture(autouse=True)
def test_setup(neo4j):
    # delete all the nodes and relations in the database
    query = "MATCH (n:p_test_branch) DETACH DELETE n"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_id_index IF EXISTS"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchIds IF EXISTS"
    neo4j.session().run(query)
    query = "DROP INDEX p_test_branch_SearchTagsIds IF EXISTS"
    neo4j.session().run(query)


def test_calling(neo4j):
    with neo4j.session() as session:
        test_parser = parser.Parser(session)
        test_parser(TEST_TAXONOMY_TXT, None, "branch", "test")

        # total number of nodes (TEXT, ENTRY, SYNONYMS, STOPWORDS) + 1 ERROR node
        query = "MATCH (n:p_test_branch) RETURN COUNT(*)"
        result = session.run(query)
        number_of_nodes = result.value()[0]
        assert number_of_nodes == 14

        # header correctly added
        query = "MATCH (n:p_test_branch) WHERE n.id = '__header__' RETURN n.preceding_lines"
        result = session.run(query)
        header = result.value()[0]
        assert header == ["# test taxonomy"]

        # synonyms correctly added
        query = "MATCH (n:p_test_branch:SYNONYMS) RETURN n ORDER BY n.src_position"
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
        query = "MATCH (n:p_test_branch:STOPWORDS) RETURN n"
        results = session.run(query)
        expected_stopwords = {
            "id": "stopwords:0",
            "tags_fr": [
                "aux",
                "au",
                "de",
                "le",
                "du",
                "la",
                "a",
                "et",
                "test normalisation",
            ],
            "tags_ids_fr": [
                "aux",
                "au",
                "de",
                "le",
                "du",
                "la",
                "a",
                "et",
                "test-normalisation",
            ],
            "preceding_lines": [],
        }
        for result in results:
            node = result.value()
            for key in expected_stopwords:
                assert node[key] == expected_stopwords[key]

        # entries correctly added
        # check for two of them
        query = """
            MATCH (n:p_test_branch:ENTRY)
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
                "preceding_lines": ["# meat ", ""],
                "prop_vegan_en": "no",
                "prop_carbon_footprint_fr_foodges_value_fr": "10",
            },
        ]
        for i, result in enumerate(results):
            node = result.value()
            for key in expected_entries[i]:
                assert node[key] == expected_entries[i][key]

        query = """
            MATCH (c:p_test_branch)-[:is_child_of]->(p:p_test_branch)
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

        query = """
            MATCH (n:p_test_branch)-[:is_before]->(p:p_test_branch)
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


def test_with_external_taxonomies(neo4j):
    with neo4j.session() as session:
        test_parser = parser.Parser(session)
        test_parser(
            TEST_TAXONOMY_TXT,
            [TEST_EXTERNAL_1_TXT, TEST_EXTERNAL_2_TXT],
            "branch",
            "test",
        )

        # total number of nodes (TEXT, ENTRY, SYNONYMS, STOPWORDS) + 1 ERROR node
        query = "MATCH (n:p_test_branch) RETURN COUNT(*)"
        result = session.run(query)
        number_of_nodes = result.value()[0]
        assert number_of_nodes == 22

        # header correctly added
        query = "MATCH (n:p_test_branch) WHERE n.id = '__header__' RETURN n.preceding_lines"
        result = session.run(query)
        header = result.value()[0]
        assert header == ["# test taxonomy"]

        # synonyms correctly added
        query = "MATCH (n:p_test_branch:SYNONYMS) RETURN n ORDER BY n.src_position"
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
        query = "MATCH (n:p_test_branch:STOPWORDS) RETURN n"
        results = session.run(query)
        expected_stopwords = {
            "id": "stopwords:0",
            "tags_fr": [
                "aux",
                "au",
                "de",
                "le",
                "du",
                "la",
                "a",
                "et",
                "test normalisation",
            ],
            "tags_ids_fr": [
                "aux",
                "au",
                "de",
                "le",
                "du",
                "la",
                "a",
                "et",
                "test-normalisation",
            ],
            "preceding_lines": [],
        }
        for result in results:
            node = result.value()
            for key in expected_stopwords:
                assert node[key] == expected_stopwords[key]

        # entries correctly added
        # check for two of them
        query = """
            MATCH (n:p_test_branch:ENTRY)
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
                "preceding_lines": ["# meat ", ""],
                "prop_vegan_en": "no",
                "prop_carbon_footprint_fr_foodges_value_fr": "10",
            },
        ]
        for i, result in enumerate(results):
            node = result.value()
            for key in expected_entries[i]:
                assert node[key] == expected_entries[i][key]

        query = """
            MATCH (c:p_test_branch)-[:is_child_of]->(p:p_test_branch)
            RETURN c.id, p.id
        """
        results = session.run(query)
        created_pairs = results.values()

        # correct number of links
        number_of_links = len(created_pairs)
        assert number_of_links == 7

        # correctly linked
        expected_pairs = [
            ["en:yogurts", "en:milk"],
            ["en:banana-yogurts", "en:yogurts"],
            ["en:passion-fruit-yogurts", "en:yogurts"],
            ["fr:yaourts-fruit-passion-alleges", "en:passion-fruit-yogurts"],
            ["en:fake-meat", "en:meat"],
            ["en:fake-duck-meat", "en:fake-meat"],
            ["en:fake-duck-meat", "en:fake-stuff"],
        ]
        for pair in created_pairs:
            assert pair in expected_pairs

        query = """
            MATCH (n:p_test_branch)-[:is_before]->(p:p_test_branch)
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


def test_error_log(neo4j, tmp_path, caplog):
    # error entries with same id
    with neo4j.session() as session:
        test_parser = parser.Parser(session)

        taxonomy_txt = textwrap.dedent(
            """
        # a fake taxonomy
        stopwords:fr: aux,au,de,le,du,la,a,et

        # meat
        en:meat

        <en:meat
        en:fake-meat

        # duplicate
        en:fake-meat
        """
        )
        taxonomy_path = tmp_path / "test.txt"
        taxonomy_path.open("w").write(taxonomy_txt)

        # parse
        with caplog.at_level(logging.ERROR):
            test_parser(str(taxonomy_path), None, "branch", "test")

        # only the 2 nodes imported, not the duplicate
        query = "MATCH (n:p_test_branch:ENTRY) RETURN COUNT(*)"
        result = session.run(query)
        number_of_nodes = result.value()[0]
        assert number_of_nodes == 2
        # error logged
        assert "WARNING: Entry with same id en:fake-meat already exists," in caplog.text
        assert "duplicate id in file at line 12" in caplog.text
        assert "The two nodes will be merged, keeping the last" in caplog.text
        assert "values in case of conflicts." in caplog.text
        # and present on project
        query = "MATCH (n:ERRORS) WHERE n.id = 'p_test_branch' RETURN n"
        results = session.run(query).value()
        node = results[0]
        assert len(node["errors"]) == 1
        error = node["errors"][0]
        assert "WARNING: Entry with same id en:fake-meat already exists," in error
        assert "duplicate id in file at line 12" in error
        assert "The two nodes will be merged, keeping the last" in error
        assert "values in case of conflicts." in error


def test_properties_confused_lang(neo4j, tmp_path):
    """Test that short property names don't get confused with language prefixes"""
    with neo4j.session() as session:
        test_parser = parser.Parser(session)
        fpath = str(
            pathlib.Path(__file__).parent.parent / "data" / "test_property_confused_lang.txt"
        )
        test_parser(fpath, None, "branch", "test")
        query = "MATCH (n:p_test_branch) WHERE n.id = 'en:1-for-planet' RETURN n"
        result = session.run(query)
        node = result.value()[0]
        # "web:en" was not confused with a language prefix "web:"
        assert "prop_web_en" in node.keys()


def test_comment_below_parent(neo4j, tmp_path):
    """Test that if a comment is below a parent, it is not added to preceeding_lines"""
    with neo4j.session() as session:
        test_parser = parser.Parser(session)
        fpath = str(pathlib.Path(__file__).parent.parent / "data" / "test_comment_below_parent.txt")
        test_parser(fpath, None, "branch", "test")
        query = "MATCH (n:p_test_branch) WHERE n.id = 'en:cow-milk' RETURN n"
        result = session.run(query)
        node = result.value()[0]
        assert node["preceding_lines"] == ["# a comment above the parent"]
        assert node["tags_en_comments"] == ["# a comment below the parent"]


def test_broken_taxonomy(neo4j, tmp_path):
    """Test that if some taxonomy lines are broken, we are able to parse it"""
    with neo4j.session() as session:
        test_parser = parser.Parser(session)
        fpath = str(pathlib.Path(__file__).parent.parent / "data" / "test_broken_taxonomy.txt")
        test_parser(fpath, None, "branch", "test")
        query = "MATCH (n:p_test_branch) WHERE n.id = 'en:milk' RETURN n"
        result = session.run(query)
        node = result.value()[0]
        assert node["prop_okprop_en"] == "this is ok"
        # isolated property
        assert node["prop_another_en"] == "this is ok too"
        query = "MATCH (n:p_test_branch) WHERE n.id = 'en:cow-milk' RETURN n"
        result = session.run(query)
        node = result.value()[0]
        assert node
        # errors are there
        query = "MATCH (n:p_test_branch:ERRORS) RETURN n"
        result = session.run(query)
        node = result.value()[0]
        assert len(node["errors"]) == 2
        assert len(node["warnings"]) == 1
