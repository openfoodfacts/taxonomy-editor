"""
Neo4J Transactions manager for DB operations
"""

import contextlib
import contextvars  # Used for creation of context vars
import logging

import neo4j  # Interface with Neo4J

from . import settings  # Neo4J settings
from .exceptions import SessionMissingError  # Custom exceptions
from .exceptions import TransactionMissingError

log = logging.getLogger(__name__)
DEFAULT_DB = "neo4j"


txn = contextvars.ContextVar("txn")
txn.set(None)

session = contextvars.ContextVar("session")
session.set(None)


@contextlib.asynccontextmanager
async def TransactionCtx():
    """
    Transaction context will set global transaction "txn" for the code in context.
    Transactions are automatically rollback if an exception occurs within the context.
    """
    global txn, session
    try:
        async with driver.session(database=DEFAULT_DB) as _session:
            txn_manager = await _session.begin_transaction()
            async with txn_manager as _txn:
                txn.set(_txn)
                session.set(_session)
                yield _txn, _session
    finally:
        txn.set(None)
        session.set(None)


@contextlib.asynccontextmanager
async def database_lifespan():
    """
    Context manager for Neo4J database
    """
    global driver
    uri = settings.uri
    driver = neo4j.AsyncGraphDatabase.driver(uri)
    try:
        yield
    finally:
        await driver.close()


def get_current_transaction():
    """
    Fetches transaction variable in current context to perform DB operations
    """
    curr_txn = txn.get()
    if curr_txn is None:
        raise TransactionMissingError()
    return curr_txn


def get_current_session():
    """
    Fetches session variable in current context to perform DB operations
    """
    curr_session = session.get()
    if curr_session is None:
        raise SessionMissingError()
    return curr_session


@contextlib.contextmanager
def SyncTransactionCtx():
    """
    Get a non async session

    BEWARE: use it with caution only for edge cases
    Normally it should be reserved to background tasks
    """
    uri = settings.uri
    driver = neo4j.GraphDatabase.driver(uri)
    with driver.session(database=DEFAULT_DB) as _session:
        yield _session
