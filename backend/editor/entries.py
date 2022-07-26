from dependencies import *

def initialize_db():
    global driver, session
    uri = settings.uri
    driver = GraphDatabase.driver(uri)
    session = driver.session()

def shutdown_db():
    session.close()
    driver.close()

def get_all_nodes(label):
    if label == "":
        query = f"""
            MATCH (n) RETURN n
        """
    else:
        query = f"""
            MATCH (n:{label}) RETURN n
        """
    result = session.run(query)
    return result

def get_nodes(label, entry):
    query = f"""
        MATCH (n:{label}) WHERE n.id = $id 
        RETURN n
    """
    result = session.run(query, {"id": entry})
    return result

def get_marginals(id):
    query = f"""
        MATCH (n:TEXT) WHERE n.id = $id
        RETURN n
    """
    result = session.run(query, {"id": id})
    return result

def update_nodes(label, entry, incomingData):
    query = f"""MATCH (n:{label}) WHERE n.id = $id"""

    for (key,value) in incomingData.items():
        query += f"""\nSET n.{key} = {value}\n"""

    query += f"""RETURN n"""

    result = session.run(query, {"id": entry})
    return result

def update_marginals(id, incomingData):
    convertedData = incomingData.dict()
    query = f"""
        MATCH (n:TEXT) WHERE n.id = $id
        SET n.preceding_lines = {str(convertedData['preceding_lines'])}
        RETURN n
    """
    result = session.run(query, {"id": id})
    return result