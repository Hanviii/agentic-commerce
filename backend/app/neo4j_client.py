import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv("backend/.env")


URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

DATABASE = "6353b728"


if not URI:
    raise ValueError("NEO4J_URI is not set")

if not USERNAME:
    raise ValueError("NEO4J_USERNAME is not set")

if not PASSWORD:
    raise ValueError("NEO4J_PASSWORD is not set")


# Accept the Neo4j Aura certificate used by this connection.
if URI.startswith("neo4j+s://"):
    URI = URI.replace("neo4j+s://", "neo4j+ssc://", 1)


class Neo4jClient:

    def __init__(self):
        self.driver = GraphDatabase.driver(
            URI,
            auth=(USERNAME, PASSWORD)
        )

    def verify_connectivity(self):
        with self.driver.session(database=DATABASE) as session:

            result = session.run(
                "RETURN 1 AS connected"
            )

            record = result.single()

            return record["connected"] == 1

    def execute_query(self, query, parameters=None):

        if parameters is None:
            parameters = {}

        with self.driver.session(database=DATABASE) as session:

            result = session.run(
                query,
                parameters
            )

            products = []

            for record in result:

                if "p" in record.keys():

                    node = record.get("p")

                    if node is not None:
                        products.append(dict(node))

                else:
                    products.append(dict(record))

            return products

    def close(self):
        self.driver.close()