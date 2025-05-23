import os
import time

import pytest
from fastapi.testclient import TestClient
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from editor import graph_db
from editor.api import app

from .test_utils import clean_neo4j_db


def pytest_addoption(parser):
    """Add an option to clean the database before running the tests

    This is useful after changes in the parser
    """
    parser.addoption("--clean-db", action="store_true", default=False)
    parser.addoption(
        "--update-test-results",
        action="store_true",
        default=False,
        help="Regenerate dumps that we use to compare test results",
    )


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def wait_neo4j():
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


@pytest.fixture(scope="session")
async def database_lifespan(wait_neo4j, anyio_backend):
    async with graph_db.database_lifespan() as driver:
        yield driver


@pytest.fixture(scope="function")
async def neo4j_session(database_lifespan, anyio_backend):
    async with graph_db.TransactionCtx() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
async def clean_db(request, database_lifespan):
    """clean_db if --clean-db was passed"""
    if request.config.getoption("--clean-db"):
        await clean_neo4j_db(database_lifespan)


@pytest.fixture(scope="session")
async def update_test_results(request, clean_db):
    """tells if --update-test-results was passed"""
    yield request.config.getoption("--update-test-results")
