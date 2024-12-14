import os
import time

import pytest
from fastapi.testclient import TestClient
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from editor.api import app
from editor import graph_db


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'

@pytest.fixture(scope="session")
def neo4j():
    """waiting for neo4j to be ready"""
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    with GraphDatabase.driver(uri) as driver:
        with driver.session() as session:
            connected = False
            while not connected:
                try:
                    session.run("MATCH () return 1 limit 1")
                except ServiceUnavailable:
                    time.sleep(1)
                else:
                    connected = True
        yield driver


@pytest.fixture(scope='session')
async def database_lifespan(neo4j):
    async with graph_db.database_lifespan() as driver:
        yield driver


@pytest.fixture
async def neo4j_session(database_lifespan, anyio_backend):
    async with graph_db.TransactionCtx() as session:
        yield session