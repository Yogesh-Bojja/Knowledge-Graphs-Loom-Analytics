from app.database import db
from app.database.get import get_entire_graph


def combine_nodes(node_id_1, node_id_2):
    # Merges 2 nodes given their ids
    query = """
        MATCH (x), (y)
        WHERE ID(x)={} AND ID(y)={}
        call apoc.refactor.mergeNodes([x,y]) YIELD node
        RETURN node
    """.format(
        node_id_1, node_id_2
    )

    with db.session() as session:
        results = session.write_transaction(lambda tx: list(tx.run(query)))

    return results


def db_rename_node(node_id, name):
    with db.session() as session:
        result = session.write_transaction(rename_node_query, node_id, name)

    return result


def db_set_node_property(node_id, key, value):
    with db.session() as session:
        result = session.write_transaction(set_node_property_query, node_id, key, value)

    return result


def db_set_relationship_property(relationship_id, key, value):
    with db.session() as session:
        result = session.write_transaction(
            set_relationship_property_query, relationship_id, key, value
        )

    return result


def db_delete_node(node_id):
    with db.session() as session:
        result = session.write_transaction(delete_node_query, node_id)

    return result


def db_remove_relationship(relation_id):
    with db.session() as session:
        result = session.write_transaction(remove_relationship_query, relation_id)

    return result


# HELPER FUNCTIONS
def rename_node_query(tx, node_id, name):
    query = """
        MATCH (n)
        WHERE ID(n)=$node_id
        SET n.name=$name
        RETURN n
    """

    result = tx.run(query, node_id=node_id, name=name)

    return result.data()


def set_node_property_query(tx, node_id, key, value):
    query = """
        MATCH (n)
        WHERE ID(n)=$node_id
        CALL apoc.create.setProperty(n, $key, $value)
        YIELD node
        RETURN node
    """

    result = tx.run(query, node_id=node_id, key=key, value=value)

    return result.data()


def set_relationship_property_query(tx, relationship_id, key, value):
    query = """
        MATCH ()-[r]-()
        WHERE ID(r)=$relationship_id
        CALL apoc.create.setRelProperty(r, $key, $value)
        YIELD rel
        RETURN rel
    """

    result = tx.run(query, relationship_id=relationship_id, key=key, value=value)

    return result.data()


def delete_node_query(tx, node_id):
    query = """
        MATCH (n) 
            WHERE ID(n)=$node_id
        OPTIONAL MATCH (n)-[r]-()
            WHERE ID(n)=$node_id
        WITH ID(r) as relation, ID(n) as node, n
        DETACH DELETE n
        RETURN node, relation
    """

    result = tx.run(query, node_id=node_id)

    return result.data()


def remove_relationship_query(tx, relation_id):
    query = """
        MATCH ()-[r]->()
        WHERE ID(r)=$relation_id
        WITH ID(r) as relation_id, r
        DELETE r
        RETURN relation_id
    """

    result = tx.run(query, relation_id=relation_id)

    return result.data()
