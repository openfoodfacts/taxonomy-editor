"""
Database helper functions for API
"""
import re
from neo4j import GraphDatabase         # Interface with Neo4J
from . import settings                  # Neo4J settings

def initialize_db():
    """
    Initialize Neo4J database
    """
    global driver, session
    uri = settings.uri
    driver = GraphDatabase.driver(uri)
    session = driver.session()

def shutdown_db():
    """
    Close session and driver of Neo4J database
    """
    session.close()
    driver.close()

def get_all_nodes(label):
    """
    Helper function used for getting all nodes with/without given label
    """
    qualifier = f":{label}" if label else ""
    query = f"""
        MATCH (n{qualifier}) RETURN n
    """
    result = session.run(query)
    return result

def get_nodes(label, entry):
    """
    Helper function used for getting the node with given id and label
    """
    query = f"""
        MATCH (n:{label}) WHERE n.id = $id 
        RETURN n
    """
    result = session.run(query, {"id": entry})
    return result

def get_parents(entry):
    """
    Helper function used for getting node parents with given id
    """
    query = f"""
        MATCH (a:ENTRY)-[r:is_child_of]->(b) WHERE a.id = $id 
        RETURN b.id
    """
    result = session.run(query, {"id": entry})
    return result

def get_children(entry):
    """
    Helper function used for getting node children with given id
    """
    query = f"""
        MATCH (b)-[r:is_child_of]->(a:ENTRY) WHERE a.id = $id 
        RETURN b.id
    """
    result = session.run(query, {"id": entry})
    return result

def update_nodes(label, entry, incomingData):
    """
    Helper function used for updation of node with given id and label
    """
    # Sanity check keys
    for key in incomingData.keys():
        if not re.match(r"^\w+$", key) or key == "id":
            raise ValueError("Invalid key: %s", key)
    
    # Get current node information and deleted keys
    curr_node = list(get_nodes(label, entry).data()[0]['n'].keys())
    deleted_keys = (set(curr_node) ^ set(incomingData))

    # Check for keys having null/empty values
    for key in curr_node:
        if (curr_node[key] == []) or (curr_node[key] == None):
            deleted_keys.add(key)

    # Build query
    query = [f"""MATCH (n:{label}) WHERE n.id = $id """]

    # Delete keys removed by user
    for key in deleted_keys:
        if key == "id": # Doesn't require to be deleted
            continue
        query.append(f"""\nREMOVE n.{key}\n""")

    # Update keys
    for key in incomingData.keys():
        query.append(f"""\nSET n.{key} = ${key}\n""")

    query.append(f"""RETURN n""")

    params = dict(incomingData, id=entry)
    result = session.run(" ".join(query), params)
    return result