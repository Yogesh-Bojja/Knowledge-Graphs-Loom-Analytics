from app.database import db


def get_entire_graph():
    with db.session() as session:
        result = session.read_transaction(get_entire_graph_query)

    # Process Results
    node_arr, relationship_arr = process_graph(result)

    return node_arr, relationship_arr


def db_get_file_details(node_id):
    with db.session() as session:
        result = session.read_transaction(get_file_details_query, node_id)

    return result


def db_get_spanning_tree(node_id):
    with db.session() as session:
        result = session.read_transaction(get_spanning_tree_query, node_id)

    node_arr, relationship_arr = process_graph(result)

    return node_arr, relationship_arr


def db_get_shortest_path(node_id_1, node_id_2):
    with db.session() as session:
        result = session.read_transaction(get_shortest_path_query, node_id_1, node_id_2)

    _, relationship_arr = process_graph(result)

    return relationship_arr


# QUERY FUNCTIONS
def get_entire_graph_query(tx):
    query = """
        MATCH (n) 
            WHERE NOT n:Outcome AND NOT n:Fact
        OPTIONAL MATCH (n)-[r]->(p) 
            WHERE NOT p:Outcome AND NOT p:Fact
        RETURN n, r, p
    """

    result = tx.run(query)

    return result.graph()


def get_file_details_query(tx, node_id):
    query = """
        MATCH (n:File)-[r:has_facts|has_outcomes]->(p)
        WHERE ID(n)=$node_id
        WITH type(r) as relation_type, p as node
        RETURN relation_type, node
    """

    result = tx.run(query, node_id=node_id)

    return result.data()


def get_spanning_tree_query(tx, node_id):
    query = """
        MATCH (p)
        WHERE ID(p)=$node_id
        CALL apoc.path.spanningTree(p, {
            labelFilter:'-Fact|-Outcome'
        })
        YIELD path
        RETURN path;
    """

    result = tx.run(query, node_id=node_id)

    return result.graph()


def get_shortest_path_query(tx, node_id_1, node_id_2):
    query = """
        MATCH (n1),(n2),
        p = shortestPath((n1)-[*]-(n2)) 
        WHERE id(n1) = $node_id_1 AND id(n2) = $node_id_2
        RETURN p
    """

    result = tx.run(query, node_id_1=node_id_1, node_id_2=node_id_2)

    return result.graph()


# HELPER FUNCTIONS
def process_graph(graph):
    node_arr = []
    for node in graph.nodes:
        node_arr.append(extract_node_info(node))

    relationship_arr = []
    for relation in graph.relationships:
        relationship_arr.append(extract_relationship_info(relation))

    return node_arr, relationship_arr


def extract_node_info(node_obj):
    node_id = node_obj.id
    node_labels = list(node_obj.labels)
    node_properties = dict(node_obj.items())

    return {"id": node_id, "labels": node_labels, "properties": node_properties}


def extract_relationship_info(relation_obj):
    relation_id = relation_obj.id
    relation_node_ids = [relation_obj.start_node.id, relation_obj.end_node.id]
    relation_type = relation_obj.type
    relation_properties = dict(relation_obj.items())

    return {
        "id": relation_id,
        "node_ids": relation_node_ids,
        "type": relation_type,
        "properties": relation_properties,
    }
