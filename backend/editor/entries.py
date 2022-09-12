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

def get_label(id):
    """
    Helper function for getting the label for a given id
    """
    if (id.startswith('stopword')): return 'STOPWORDS'
    elif (id.startswith('synonym')): return 'SYNONYMS'
    elif (id.startswith('__header__') or id.startswith('__footer__')): return 'TEXT'
    else: return 'ENTRY'

def create_node(label, entry, mainLanguageCode):
    """
    Helper function used for creating a node with given id and label
    """
    query = [f"""CREATE (n:{label})\n"""]

    # Build all basic keys of a node
    if (label == "ENTRY"):
        canonicalTag = entry[3:]
        query.append(f""" SET n.main_language = "{mainLanguageCode}" """) # Required for only an entry
    else:
        canonicalTag = ""

    query.append(f""" SET n.id = $id """)
    query.append(f""" SET n.tags_{mainLanguageCode} = ["{canonicalTag}"] """)
    query.append(f""" SET n.preceding_lines = [] """)

    result = session.run(" ".join(query), {"id": entry})
    return result

def add_node_to_end(label, entry):
    """
    Helper function which adds an existing node to end of taxonomy
    """
    # Delete relationship between current last node and __footer__
    query = [f"""MATCH (a)-[r:is_before]->(b:TEXT) WHERE b.id = "__footer__" DELETE r\n"""]
    query.append(f"""RETURN a""")
    result = session.run(" ".join(query))
    end_node = result.data()[0]['a']
    end_node_label = get_label(end_node['id']) # Get current last node ID

    # Rebuild relationships by inserting incoming node at the end
    query = []
    query.append(f"""MATCH (n:{label}) WHERE n.id = $id\n""")
    query.append(f"""MATCH (b:{end_node_label}) WHERE b.id = $endnodeid\n""")
    query.append(f"""MATCH (a:TEXT) WHERE a.id = "__footer__"\n""")
    query.append(f"""CREATE (b)-[:is_before]->(n)\n""")
    query.append(f"""CREATE (n)-[:is_before]->(a)""")
    result = session.run(" ".join(query), {"id": entry, "endnodeid": end_node['id']})

def add_node_to_beginning(label, entry):
    """
    Helper function which adds an existing node to beginning of taxonomy
    """
    # Delete relationship between current first node and __header__
    query = [f"""MATCH (b:TEXT)-[r:is_before]->(a) WHERE b.id = "__header__" DELETE r\n"""]
    query.append(f"""RETURN a""")
    result = session.run(" ".join(query))
    end_node = result.data()[0]['a']
    end_node_label = get_label(end_node['id']) # Get current first node ID

    # Rebuild relationships by inserting incoming node at the beginning
    query = []
    query.append(f"""MATCH (n:{label}) WHERE n.id = $id\n""")
    query.append(f"""MATCH (b:{end_node_label}) WHERE b.id = $startnodeid\n""")
    query.append(f"""MATCH (a:TEXT) WHERE a.id = "__header__"\n""")
    query.append(f"""CREATE (n)-[:is_before]->(b)\n""")
    query.append(f"""CREATE (a)-[:is_before]->(n)""")
    result = session.run(" ".join(query), {"id": entry, "startnodeid": end_node['id']})

def delete_node(label, entry):
    """
    Helper function used for deleting a node with given id and label
    """
    # Finding node to be deleted using node ID
    query = []
    query.append(f"""MATCH (n:{label})-[:is_before]->(a) WHERE n.id = $id\n""")
    query.append(f"""MATCH (b)-[:is_before]->(n)\n""")
    query.append(f"""DETACH DELETE (n)""")

    # Rebuild relationships after deletion
    query.append(f"""CREATE (b)-[:is_before]->(a)""") 

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
    
    # Get current node information and deleted keys
    curr_node = get_nodes(label, entry).data()[0]['n']
    curr_node_keys = list(curr_node.keys())
    deleted_keys = (set(curr_node_keys) ^ set(incomingData))

    # Check for keys having null/empty values
    for key in curr_node_keys:
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
        main_language_code = child[:2]
        is_old_node = list(get_nodes("ENTRY", child))

        # Create node if not exists
        if (not is_old_node):
            create_node("ENTRY", child, main_language_code)
            add_node_to_end("ENTRY", child)

        # Delete relationships of deleted child node
        else:
            query.append(f""" MATCH (a:ENTRY)-[rel:is_child_of]->(b:ENTRY) WHERE b.id = $id AND a.id = "{child}"\n """)
            query.append(f""" DELETE rel """)
            session.run(" ".join(query), {"id": entry})
    
    # Stores result of last query executed
    result = []
    for child in incomingData:
        query = []
        # Create new relationships if exists
        query.append(f""" MATCH (a:ENTRY), (b:ENTRY) WHERE a.id = $id AND b.id = "{child}"\n """)
        query.append(f""" MERGE (b)-[r:is_child_of]->(a) """)
        result = session.run(" ".join(query), {"id": entry})
    
    return result