from neo4j import GraphDatabase         # Interface with Neo4J
from . import settings                  # Neo4J settings

txn = None

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