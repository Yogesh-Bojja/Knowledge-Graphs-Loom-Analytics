# Note: request.args.get() for GET request, request.form.get() for POST request

from app.graph import bp
from app.database.create import db_create_node, create_single_relationship
from app.database.get import (
    get_entire_graph,
    db_get_file_details,
    db_get_spanning_tree,
    db_get_shortest_path,
)
from app.database.modify import (
    combine_nodes,
    db_rename_node,
    db_delete_node,
    db_remove_relationship,
    db_set_node_property,
    db_set_relationship_property,
)

from flask import request, render_template


@bp.route("/view")
def view_graph():
    return render_template("graph.html")


@bp.route("/init_graph", methods=["POST"])
def init_graph():
    node_arr, relation_arr = get_entire_graph()

    return {"nodes": node_arr, "relations": relation_arr}


@bp.route("/create_node", methods=["POST"])
def create_node():
    node_type = request.form.get("node_type")
    name = request.form.get("name")

    if not (name and node_type):
        return "Error in request", 400

    props = {"name": name}

    node_id = db_create_node(node_type, props, {})

    return {"new_node_id": node_id}


@bp.route("/rename_node", methods=["POST"])
def rename_node():
    node_id = request.form.get("node_id")
    name = request.form.get("name")

    if not (node_id and name):
        return "Error in request", 400

    result = db_rename_node(int(node_id), name)

    if len(result):
        return "OK", 200
    else:
        return "Node not found", 400


@bp.route("/set_node_property", methods=["POST"])
def set_node_property():
    node_id = request.form.get("node_id")
    key = request.form.get("key")
    value = request.form.get("value")

    if not (node_id and key and value):
        return "Error in request", 400

    result = db_set_node_property(int(node_id), key, value)

    if len(result):
        return "OK", 200
    else:
        return "Node not found", 400


@bp.route("/set_relationship_property", methods=["POST"])
def set_relationship_property():
    relationship_id = request.form.get("relationship_id")
    key = request.form.get("key")
    value = request.form.get("value")

    if not (relationship_id and key and value):
        return "Error in request", 400

    result = db_set_relationship_property(int(relationship_id), key, value)

    if len(result):
        return "OK", 200
    else:
        return "Relationship not found", 400


@bp.route("/remove_node", methods=["POST"])
def remove_node():
    node_id = request.form.get("node_id")

    if not node_id:
        return "Error in request", 400

    result = db_delete_node(int(node_id))

    if len(result):
        arr = []

        for record in result:
            arr.append(record["relation"])

        return {"remove_relationships": arr}
    else:
        return "Node not found", 400


@bp.route("/merge_nodes", methods=["POST"])
def merge_nodes():
    node_1_id = request.form.get("node_id_1")
    node_2_id = request.form.get("node_id_2")

    result = combine_nodes(node_1_id, node_2_id)

    if result:
        return "OK", 200
    else:
        return "Nodes not found", 400


@bp.route("/create_relationship", methods=["POST"])
def add_relationship():
    node_id_1 = request.form.get("node_id_1")
    node_id_2 = request.form.get("node_id_2")
    relation_type = request.form.get("relation_type")

    if not (node_id_1 and node_id_2 and relation_type):
        return "Error in request", 400

    relation_id = create_single_relationship(
        int(node_id_1), int(node_id_2), relation_type
    )

    return {"new_relation_id": relation_id}


@bp.route("/remove_relationship", methods=["POST"])
def remove_relationship():
    relation_id = request.form.get("relation_id")

    if not relation_id:
        return "Error in request", 400

    result = db_remove_relationship(int(relation_id))

    if result:
        return "OK", 200
    else:
        return "Relationship not found", 400


@bp.route("/get_file_details", methods=["POST"])
def get_file_details():
    node_id = request.form.get("node_id")

    if not node_id:
        return "Error in request", 400

    result = db_get_file_details(int(node_id))

    if result:
        return {"result": result}
    else:
        return "Node not found or is not a citation", 400


@bp.route("/spanning_tree", methods=["POST"])
def spanning_tree():
    node_id = request.form.get("node_id")

    if not node_id:
        return "Error in request", 400

    node_arr, relation_arr = db_get_spanning_tree(int(node_id))

    return {"nodes": node_arr, "relations": relation_arr}


@bp.route("/get_shortest_path", methods=["POST"])
def shortest_path():
    node_id_1 = request.form.get("node_id_1")
    node_id_2 = request.form.get("node_id_2")

    if not (node_id_1 and node_id_2):
        return "Error in request", 400

    result = db_get_shortest_path(int(node_id_1), int(node_id_2))

    return {"relations": result}
