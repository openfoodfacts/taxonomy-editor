"""
Neo4J Transactions manager for DB operations
"""
import contextlib
import contextvars
from neo4j import GraphDatabase                     # Interface with Neo4J
from . import settings                              # Neo4J settings
from .exceptions import TransactionMissingError     # Custom exceptions

txn = contextvars.ContextVar('txn')
txn.set(None)

@contextlib.contextmanager
def TransactionCtx():
    """
    Transaction context will set global transaction "txn" for the code in context
    Transactions are automatically rollbacked if an exception occurs within the context
    """
    global txn
    with driver.session() as session:
        with session.begin_transaction() as _txn:
            txn.set(_txn)
            yield txn
    txn.set(None)

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
    curr_txn = txn.get()
    if (curr_txn == None):
        raise TransactionMissingError()
    return curr_txn