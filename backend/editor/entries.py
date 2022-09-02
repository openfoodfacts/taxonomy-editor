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

def create_node(label, entry):
    """
    Helper function used for creating a node with given id and label
    """
    query = [f"""CREATE (n:{label})\n """]

    # Build all basic keys of a node
    mainLanguageCode = entry[:2]
    canonicalTag = entry[3:]
    query.append(f""" SET n.id = $id """)
    query.append(f""" SET n.tags_{mainLanguageCode} = ["{canonicalTag}"] """)
    query.append(f""" SET n.main_language = "{mainLanguageCode}" """)
    query.append(f""" SET n.preceding_lines = [] """)
    query.append(f""" RETURN n """)

    result = session.run(" ".join(query), {"id": entry})
    return result

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
    
    # Build query
    query = [f"""MATCH (n:{label}) WHERE n.id = $id """, """SET n={} """, """SET n.id = $id"""]

    for key in incomingData.keys():
        query.append(f"""\nSET n.{key} = ${key}\n""")

    query.append(f"""RETURN n""")

    params = dict(incomingData, id=entry)
    result = session.run(" ".join(query), params)
    return result

def update_node_children(entry, incomingData):
    """
    Helper function used for updation of node children with given id 
    """
    # Parse node ids from Neo4j Record object
    current_children = [record["b.id"] for record in list(get_children(entry))]
    deleted_children = list(set(current_children) ^ set(incomingData))

    # Delete relationships
    for child in deleted_children:
        query = []
        is_old_node = list(get_nodes("ENTRY", child))

        # Create node if not exists
        if (not is_old_node):
            create_node("ENTRY", child)

        # Delete relationships of deleted child node
        else:
            query.append(f""" MATCH (a:ENTRY)-[rel:is_child_of]->(b:ENTRY) WHERE b.id = $id AND a.id = "{child}"\n """)
            query.append(f""" DELETE rel """)
            session.run(" ".join(query), {"id": entry})
    
    # Stores result of last query executed
    result = None
    for child in incomingData:
        query = []
        # Create new relationships if exists
        query.append(f""" MATCH (a:ENTRY), (b:ENTRY) WHERE a.id = $id AND b.id = "{child}"\n """)
        query.append(f""" MERGE (b)-[r:is_child_of]->(a) """)
        result = session.run(" ".join(query), {"id": entry})
    
    return result