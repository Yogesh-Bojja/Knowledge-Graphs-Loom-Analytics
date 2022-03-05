from neo4j import GraphDatabase

from app import app

db = GraphDatabase.driver(
    app.config["DB_URI"], auth=(app.config["DB_USER"], app.config["DB_PASS"])
)
