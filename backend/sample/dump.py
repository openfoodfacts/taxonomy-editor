#!/usr/bin/env python3
"""A script to dump a Neo4J database to a JSON file."""
import argparse
import json
import os

from neo4j import GraphDatabase

DEFAULT_URL = os.environ.get("NEO4J_URI", "bolt://localhost:7687")


def get_session(uri=DEFAULT_URL):
    """Get a session object for the Neo4J database."""
    return GraphDatabase.driver(uri).session()


def dump_nodes(session, file):
    """Dump all nodes from the database to a JSON file."""
    node_count = session.run("MATCH (n) RETURN count(n)").single()[0]
    for i, node in enumerate(session.run("MATCH (n) RETURN n")):
        node_dict = dict(node["n"])
        labels_list = list(node["n"].labels)
        node_dict["labels"] = labels_list
        if i < node_count - 1:
            file.write(json.dumps(node_dict, ensure_ascii=False, default=str) + ",")
        else:
            file.write(json.dumps(node_dict, ensure_ascii=False, default=str))


def dump_relations(session, file):
    """Dump all relationships from the database to a JSON file."""
    rels_count = session.run("MATCH (n)-[r]->(m) RETURN count(r)").single()[0]
    for i, rel in enumerate(session.run("MATCH (n)-[r]->(m) RETURN r")):
        start_node_id = rel["r"].nodes[0].id
        end_node_id = rel["r"].nodes[1].id
        start_node = session.run(
            "MATCH (n) WHERE id(n) = $id RETURN n", {"id": start_node_id}
        ).single()["n"]["id"]
        end_node = session.run(
            "MATCH (n) WHERE id(n) = $id RETURN n", {"id": end_node_id}
        ).single()["n"]["id"]
        rel_dict = {rel["r"].type: [start_node, end_node]}
        if i < rels_count - 1:
            file.write(json.dumps(rel_dict, ensure_ascii=False) + ",")
        else:
            file.write(json.dumps(rel_dict, ensure_ascii=False))


def get_options(args=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Dump Neo4J database to JSON file")
    parser.add_argument("--url", default=DEFAULT_URL, help="Neo4J database bolt URL")
    parser.add_argument("file", help="JSON file name to dump")
    return parser.parse_args(args)


def dump_db(file_path, url=DEFAULT_URL):
    session = get_session(url)
    with open(file_path, "w") as f:
        f.write('{"nodes": [')
        dump_nodes(session, f)
        f.write('], "relations": [')
        dump_relations(session, f)
        f.write("]}")


if __name__ == "__main__":
    options = get_options()
    dump_db(file_path=options.file, url=options.url)
