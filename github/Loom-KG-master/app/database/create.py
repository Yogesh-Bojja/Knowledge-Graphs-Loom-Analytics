from app.database import db


def db_create_node(node_type, identity_prop, props):
    # Create node without any relationships
    with db.session() as session:
        result = session.write_transaction(
            create_node_query, node_type, identity_prop, props
        )

    return result[0]["node_id"]


def db_create_relations(node_name, node_type, ident_props, props, relation_type):
    with db.session() as session:
        result = session.write_transaction(
            create_relation_query,
            node_name,
            node_type,
            ident_props,
            props,
            relation_type,
        )

    return result


def create_single_relationship(node_id_1, node_id_2, relation_type):
    with db.session() as session:
        try:
            relation_id = session.write_transaction(
                create_single_relationship_query, node_id_1, node_id_2, relation_type
            )

            return relation_id
        except:
            # Node ids likely don't exist in database
            return 0


def create_fact_node(props, citation_no):
    return db_create_relations(
        citation_no,
        "Fact",
        {"name": "fact", "for_citation": citation_no},
        props,
        "has_facts",
    )


def create_outcome_node(props, citation_no):
    return db_create_relations(
        citation_no,
        "Outcome",
        {"name": "outcome", "for_citation": citation_no},
        props,
        "has_outcomes",
    )


# HELPER FUNCTIONS
def create_relation_query(
    tx, node_name, node_type, identity_props, props, relation_type
):
    query = """
        MATCH (f:File) WHERE f.name = $node_name
        CALL apoc.merge.node([$node_type], $identity_props, $props) YIELD node as p
        CALL apoc.merge.relationship(f, $relation_type, {}, {}, p ) YIELD rel as r
        RETURN p, r, f
    """

    result = tx.run(
        query,
        node_name=node_name,
        node_type=node_type,
        relation_type=relation_type,
        identity_props=identity_props,
        props=props,
    )

    return result.data()


def create_node_query(tx, node_type, identity_prop, props):
    query = """
        CALL apoc.merge.node([$node_type], $identity_prop, $props, $props) 
        YIELD node
        RETURN ID(node) AS node_id
    """

    result = tx.run(
        query, node_type=node_type, identity_prop=identity_prop, props=props
    )

    # Return id of existing or newly created node. To be appropriately handled client-side
    return result.data()


def create_single_relationship_query(tx, node_id_1, node_id_2, relation_type):
    query = """
        MATCH (n1) WHERE ID(n1) = $node_id_1
        OPTIONAL MATCH (n2) WHERE ID(n2) = $node_id_2
        CALL apoc.merge.relationship(n1, $relation_type, { }, { }, n2) YIELD rel as r
        return ID(r) as relation_id
    """

    result = tx.run(
        query, node_id_1=node_id_1, node_id_2=node_id_2, relation_type=relation_type
    )

    return result.data()[0]["relation_id"]
