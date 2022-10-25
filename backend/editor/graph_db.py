"""
Neo4J Transactions manager for DB operations
"""
import contextlib
import contextvars                                                          # Used for creation of context vars

from neo4j import GraphDatabase                                             # Interface with Neo4J
from . import settings                                                      # Neo4J settings

from .exceptions import SessionMissingError, TransactionMissingError        # Custom exceptions

txn = contextvars.ContextVar('txn')
txn.set(None)

session = contextvars.ContextVar('session')
session.set(None)

@contextlib.contextmanager
def TransactionCtx():
    """
    Transaction context will set global transaction "txn" for the code in context.
    Transactions are automatically rollback if an exception occurs within the context.
    """
    global txn, session
    with driver.session() as _session:
        with _session.begin_transaction() as _txn:
            txn.set(_txn)
            session.set(_session)
            yield txn, session
    txn.set(None)
    session.set(None)

def initialize_db():
    """
    Initialize Neo4J database
    """
    global driver
    uri = settings.uri
    driver = GraphDatabase.driver(uri)

def shutdown_db():
    """
    Close session and driver of Neo4J database
    """
    driver.close()

def get_current_transaction():
    """
    Fetches transaction variable in current context to perform DB operations
    """
    curr_txn = txn.get()
    if (curr_txn == None):
        raise TransactionMissingError()
    return curr_txn


def get_current_session():
    """
    Fetches session variable in current context to perform DB operations
    """
    curr_session = session.get()
    if (curr_session == None):
        raise SessionMissingError()
    return curr_session