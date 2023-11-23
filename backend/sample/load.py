#!/usr/bin/env python3
"""A simple script to load a jsonl into the Neo4J Database
"""
import argparse
import json
import os
import sys
from datetime import datetime

from neo4j import GraphDatabase

DEFAULT_URL = os.environ.get("NEO4J_URI", "bolt://localhost:7687")


def get_session(uri=DEFAULT_URL):
    return GraphDatabase.driver(uri).session()


def clean_db(session):
    session.run("""match (p) detach delete(p)""")


def add_node(node, session):
    labels = node.pop("labels", [])
    if "created_at" in node:
        # Truncate the microseconds to six digits to match the format string
        stringified_datetime = node["created_at"][:26] + node["created_at"][29:]
        node["created_at"] = datetime.strptime(stringified_datetime, "%Y-%m-%dT%H:%M:%S.%f%z")
    query = f"CREATE (n:{':'.join(labels)} $data)"
    session.run(query, data=node)


def add_link(rel, session):
    if len(rel) != 1 and len(next(iter(rel.values()))) != 2:
        raise ValueError(
            f"""
            Expecting relations to by dict like {{"rel_name": ["node1", "node2"]}}, got {rel}
        """.trim()
        )
    for rel_name, (from_id, to_id) in rel.items():
        query = f"""
        MATCH(source) WHERE source.id = $from_id
        MATCH(target) WHERE target.id = $to_id
        CREATE (source)-[:{rel_name}]->(target)
        """
        session.run(query, {"from_id": from_id, "to_id": to_id})


def load_jsonl(file_path, session):
    data = json.load(open(file_path))
    for node in data.pop("nodes"):
        add_node(node, session)
    for rel in data.pop("relations"):
        add_link(rel, session)
    if data:
        print(f"Unprocessed data: {data}", file=sys.stderr)


def get_options(args=None):
    parser = argparse.ArgumentParser(description="Import json file to Neo4J database")
    parser.add_argument("--url", default=DEFAULT_URL, help="Neo4J database bolt URL")
    parser.add_argument("file", help="Json file to import")
    parser.add_argument(
        "--reset", default=False, action="store_true", help="Clean all database before importing"
    )
    parser.add_argument(
        "--yes", default=False, action="store_true", help="Assume yes to all questions"
    )
    return parser.parse_args(args)


def confirm_clean_db(session):
    num_nodes = session.run("""match (p) return count(*)""").value()[0]
    if not num_nodes:
        return True
    response = input(f"You are about to remove {num_nodes} nodes, are you sure ? [y/N]: ")
    return response.lower() in ("y", "yes")


if __name__ == "__main__":
    options = get_options()
    session = get_session(options.url)
    if options.reset:
        confirmed = options.yes or confirm_clean_db(session)
        if not confirmed:
            sys.exit(1)
        else:
            clean_db(session)
    load_jsonl(options.file, session)
