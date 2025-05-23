"""Some utils related to testing
"""

# IMPORTANT: this file is named test_utils to have "magic" assert from pytest works
# and it also have a test inside

import difflib
import inspect
import io
import json
import re

from sample.dump import dump_db_to_buffer
from sample.load import load_file


class FakeBackgroundTask:
    """A fake background task to avoid running background tasks during tests"""

    def __init__(self):
        self.tasks = []

    def add_task(self, fn, *args, **kwargs):
        self.tasks.append((fn, args, kwargs))

    async def run(self):
        while self.tasks:
            fn, args, kwargs = self.tasks.pop()
            if inspect.iscoroutinefunction(fn):
                await fn(*args, **kwargs)
            else:
                fn(*args, **kwargs)


async def clean_neo4j_db(neo4j):
    """Delete all nodes and relations in the database"""
    async with neo4j.session() as session:
        query = "MATCH (n) DETACH DELETE n"
        await session.run(query)
        # list all indexes and drop them
        query = """
            SHOW INDEXES
            YIELD name AS idxname
            RETURN idxname
        """
        indexes = await session.run(query)
        for index in await indexes.values():
            query = f"DROP INDEX {index[0]} IF EXISTS"
            await session.run(query)


TIMESTAMP_RE = re.compile(r"^\d{4}-[0-1]\d-[0-3]\dT[0-2]\d:[0-6]\d:[0-6]\d(\.[\d+:]+)*$")


def make_dump_comparable(data, check=True):
    """Makes two dumps comparable,

    :param bool check: does some check on data
    """
    for node in data["nodes"]:
        # Label order does not matter: make it a set
        node["labels"] = set(node["labels"])
        if node.get("created_at"):
            # created_at will change: remove it
            if check:
                # assert it's a timestamp
                assert TIMESTAMP_RE.match(
                    node["created_at"]
                ), f"created_at is not a timestamp: {node['created_at']}"
            node["created_at"] = "--date--"
    # Relation order does not matter: sort relations
    data["relations"].sort(key=json.dumps)
    return data


def compare_db_with_dump(dump_path, update_test_results):
    """Compare the Neo4j database with the dumped JSON file."""
    if not dump_path.startswith("sample/"):
        dump_path = "tests/expected_results/" + dump_path
    buffer = io.StringIO()
    dump_db_to_buffer(buffer)
    db_data = json.loads(buffer.getvalue())
    del buffer
    if update_test_results:
        # regenerate test data
        with open(dump_path, "w") as f:
            json.dump(db_data, f, indent=2, sort_keys=True)
        return db_data, db_data
    test_data = json.load(open(dump_path))
    make_dump_comparable(test_data, check=False)
    make_dump_comparable(db_data)
    assert test_data, db_data


def match_taxonomy(content, taxonomy_path):
    assert content.splitlines(True) == open(taxonomy_path).readlines()


def compare_taxonomy(content, taxonomy_path, diff_path, update_test_results):
    if not diff_path.startswith("sample/"):
        diff_path = "tests/expected_results/" + diff_path
    # compare to original taxonomy
    differences = difflib.unified_diff(
        open(taxonomy_path).readlines(),
        content.splitlines(True),
    )
    diff_txt = "".join(differences)
    if update_test_results:
        with open(diff_path, "w") as f:
            f.write(diff_txt)
        return
    expected = open(diff_path).read()
    assert diff_txt == expected


def test_load_and_dump():
    """Here we are testing the tool"""
    # Path to the test data JSON file
    test_data_path = "sample/dumped-test-taxonomy.json"

    # Run load.py to import data into Neo4j database
    load_file(test_data_path)

    compare_db_with_dump(test_data_path, update_test_results=False)
