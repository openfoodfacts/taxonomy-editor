import os
import time

import pytest
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable


@pytest.fixture
def neo4j():
    """waiting for neo4j to be ready"""
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    driver = GraphDatabase.driver(uri)
    session = driver.session()
    connected = False
    while not connected:
        try:
            session.run("MATCH () return 1 limit 1")
        except ServiceUnavailable:
            time.sleep(1)
        else:
            connected = True
    return driver
