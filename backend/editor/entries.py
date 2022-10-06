"""
Database helper functions for API
"""
import re
from .graph_db import get_current_transaction   # Neo4J transactions helper
from .normalizer import normalizing             # Normalizing tags

def get_label(id):
    """
    Helper function for getting the label for a given id
    """
    if (id.startswith('stopword')): return 'STOPWORDS'
    elif (id.startswith('synonym')): return 'SYNONYMS'
    elif (id.startswith('__header__') or id.startswith('__footer__')): return 'TEXT'
    else: return 'ENTRY'

def create_node(label, entry, main_language_code, multi_label):
    """
    Helper function used for creating a node with given id and label
    """
    query = [f"""CREATE (n:{multi_label}:{label})\n"""]
    params = {"id": entry}

    # Build all basic keys of a node
    if (label == "ENTRY"):
        canonical_tag = entry.split(":", 1)[1]
        query.append(f""" SET n.main_language = $main_language_code """) # Required for only an entry
        params["main_language_code"] = main_language_code
    else:
        canonical_tag = ""

    query.append(f""" SET n.id = $id """)
    query.append(f""" SET n.tags_{main_language_code} = [$canonical_tag] """)
    query.append(f""" SET n.preceding_lines = [] """)

    params["canonical_tag"] = canonical_tag
    result = get_current_transaction().run(" ".join(query), params)
    return result

def add_node_to_end(label, entry, multi_label):
    """
    Helper function which adds an existing node to end of taxonomy
    """
    # Delete relationship between current last node and __footer__
    query = f"""
       MATCH (last_node)-[r:is_before]->(footer:{multi_label}:TEXT) WHERE footer.id = "__footer__" DELETE r 
       RETURN last_node
    """
    result = get_current_transaction().run(query)
    end_node = result.data()[0]['last_node']
    end_node_label = get_label(end_node['id']) # Get current last node ID

    # Rebuild relationships by inserting incoming node at the end
    query = []
    query = f"""
        MATCH (new_node:{multi_label}:{label}) WHERE new_node.id = $id
        MATCH (last_node:{multi_label}:{end_node_label}) WHERE last_node.id = $endnodeid
        MATCH (footer:{multi_label}:TEXT) WHERE footer.id = "__footer__"
        CREATE (last_node)-[:is_before]->(new_node)
        CREATE (new_node)-[:is_before]->(footer)
    """
    result = get_current_transaction().run(query, {"id": entry, "endnodeid": end_node['id']})

def add_node_to_beginning(label, entry, multi_label):
    """
    Helper function which adds an existing node to beginning of taxonomy
    """
    # Delete relationship between current first node and __header__
    query = f"""
        MATCH (header:{multi_label}:TEXT)-[r:is_before]->(first_node) WHERE header.id = "__header__" DELETE r
        RETURN first_node
    """
    result = get_current_transaction().run(query)
    start_node = result.data()[0]['first_node']
    start_node_label = get_label(start_node['id']) # Get current first node ID

    # Rebuild relationships by inserting incoming node at the beginning
    query= f"""
        MATCH (new_node:{multi_label}:{label}) WHERE new_node.id = $id
        MATCH (first_node:{multi_label}:{start_node_label}) WHERE first_node.id = $startnodeid
        MATCH (header:{multi_label}:TEXT) WHERE header.id = "__header__"
        CREATE (new_node)-[:is_before]->(first_node)
        CREATE (header)-[:is_before]->(new_node)
    """
    result = get_current_transaction().run(query, {"id": entry, "startnodeid": start_node['id']})

def delete_node(label, entry, multi_label):
    """
    Helper function used for deleting a node with given id and label
    """
    # Finding node to be deleted using node ID
    query = f"""
        // Find node to be deleted using node ID
        MATCH (deleted_node:{multi_label}:{label})-[:is_before]->(next_node) WHERE deleted_node.id = $id
        MATCH (previous_node)-[:is_before]->(deleted_node)
        // Remove node
        DETACH DELETE (deleted_node)
        // Rebuild relationships after deletion
        CREATE (previous_node)-[:is_before]->(next_node)
    """
    result = get_current_transaction().run(query, {"id": entry})
    return result

def get_all_nodes(label, multi_label):
    """
    Helper function used for getting all nodes with/without given label
    """
    qualifier = f":{label}" if label else ""
    query = f"""
        MATCH (n:{multi_label}{qualifier}) RETURN n
    """
    result = get_current_transaction().run(query)
    return result

def get_nodes(label, entry, multi_label):
    """
    Helper function used for getting the node with given id and label
    """
    query = f"""
        MATCH (n:{multi_label}:{label}) WHERE n.id = $id 
        RETURN n
    """
    result = get_current_transaction().run(query, {"id": entry})
    return result

def get_parents(entry, multi_label):
    """
    Helper function used for getting node parents with given id
    """
    query = f"""
        MATCH (child_node:{multi_label}:ENTRY)-[r:is_child_of]->(parent) WHERE child_node.id = $id 
        RETURN parent.id
    """
    result = get_current_transaction().run(query, {"id": entry})
    return result

def get_children(entry, multi_label):
    """
    Helper function used for getting node children with given id
    """
    query = f"""
        MATCH (child)-[r:is_child_of]->(parent_node:{multi_label}:ENTRY) WHERE parent_node.id = $id 
        RETURN child.id
    """
    result = get_current_transaction().run(query, {"id": entry})
    return result

def update_nodes(label, entry, new_node_keys, multi_label):
    """
    Helper function used for updation of node with given id and label
    """
    # Sanity check keys
    for key in new_node_keys.keys():
        if not re.match(r"^\w+$", key) or key == "id":
            raise ValueError("Invalid key: %s", key)
    
    # Get current node information and deleted keys
    curr_node = get_nodes(label, entry, multi_label).data()[0]['n']
    curr_node_keys = list(curr_node.keys())
    deleted_keys = (set(curr_node_keys) ^ set(new_node_keys))

    # Check for keys having null/empty values
    for key in curr_node_keys:
        if (curr_node[key] == []) or (curr_node[key] == None):
            deleted_keys.add(key)

    # Build query
    query = [f"""MATCH (n:{multi_label}:{label}) WHERE n.id = $id """]

    # Delete keys removed by user
    for key in deleted_keys:
        if key == "id": # Doesn't require to be deleted
            continue
        query.append(f"""\nREMOVE n.{key}\n""")

    # Update keys
    for key in new_node_keys.keys():
        query.append(f"""\nSET n.{key} = ${key}\n""")

    query.append(f"""RETURN n""")

    params = dict(new_node_keys, id=entry)
    result = get_current_transaction().run(" ".join(query), params)
    return result

def update_node_children(entry, new_children_ids, multi_label):
    """
    Helper function used for updation of node children with given id 
    """
    # Parse node ids from Neo4j Record object
    current_children = [record["child.id"] for record in list(get_children(entry, multi_label))]
    deleted_children = set(current_children) - set(new_children_ids)
    added_children = set(new_children_ids) - set(current_children)

    # Delete relationships
    for child in deleted_children:
        query = f""" 
            MATCH (deleted_child:{multi_label}:ENTRY)-[rel:is_child_of]->(parent:{multi_label}:ENTRY) 
            WHERE parent.id = $id AND deleted_child.id = $child
            DELETE rel
        """
        get_current_transaction().run(query, {"id": entry, "child": child})

    # Create non-existing nodes
    query = f"""MATCH (child:{multi_label}:ENTRY) WHERE child.id in $ids RETURN child.id"""
    existing_ids = [record['child.id'] for record in get_current_transaction().run(query, ids=list(added_children))]
    to_create = added_children - set(existing_ids)

    for child in to_create:
        main_language_code = child.split(":", 1)[0]
        create_node("ENTRY", child, main_language_code, multi_label)
        
        # TODO: We would prefer to add the node just after its parent entry
        add_node_to_end("ENTRY", child, multi_label)

    # Stores result of last query executed
    result = []
    for child in added_children:
        # Create new relationships if it doesn't exist
        query = f"""
            MATCH (parent:{multi_label}:ENTRY), (new_child:{multi_label}:ENTRY) 
            WHERE parent.id = $id AND new_child.id = $child
            MERGE (new_child)-[r:is_child_of]->(parent)
        """
        result = get_current_transaction().run(query, {"id": entry, "child": child})
    
    return result

def full_text_search(text, branch, taxonomy):
    """
    Helper function used for searching a taxonomy
    """
    # Escape special characters
    normalized_text = re.sub(r"[^A-Za-z0-9_]", r" ", text)
    normalized_id_text = normalizing(text)

    multi_label = ('t_'+taxonomy)+'_'+('b_'+branch)
    id_index = multi_label+'_SearchIds'
    tags_index = multi_label+'_SearchTags'

    text_query_exact = "*" + normalized_text + '*'
    text_query_fuzzy = normalized_text + "~"
    text_id_query_fuzzy = normalized_id_text + "~"
    text_id_query_exact = "*" + normalized_id_text + "*"
    params = {
        "id_index" : id_index,
        "tags_index" : tags_index,
        "text_query_fuzzy" : text_query_fuzzy,
        "text_query_exact" : text_query_exact,
        "text_id_query_fuzzy" : text_id_query_fuzzy,
        "text_id_query_exact" : text_id_query_exact 
    }

    # Fuzzy search and wildcard (*) search on two indexes
    # Fuzzy search has more priority, since it matches more close strings
    # IDs are given slightly lower priority than tags in fuzzy search
    query = """
        CALL {
                CALL db.index.fulltext.queryNodes($id_index, $text_id_query_fuzzy)
                yield node, score as score_
                return node, score_ * 3 as score
            UNION
                CALL db.index.fulltext.queryNodes($tags_index, $text_query_fuzzy)
                yield node, score as score_
                return node, score_ * 5 as score
            UNION
                CALL db.index.fulltext.queryNodes($id_index, $text_id_query_exact)
                yield node, score as score_
                return node, score_ as score
            UNION
                CALL db.index.fulltext.queryNodes($tags_index, $text_query_exact)
                yield node, score as score_
                return node, score_ as score 
        }
        with node.id as node, score
        RETURN node, sum(score) as score
        
        ORDER BY score DESC
    """
    result = [record["node"] for record in get_current_transaction().run(query, params)]
    return result