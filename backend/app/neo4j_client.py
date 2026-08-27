import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv("backend/.env")

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Use the SSL mode that worked during our connection test
URI = URI.replace("neo4j+s://", "neo4j+ssc://")


class Neo4jClient:

    def __init__(self):
        self.driver = GraphDatabase.driver(
            URI,
            auth=(USERNAME, PASSWORD)
        )

    def execute_query(self, query, parameters):
        with self.driver.session() as session:
            result = session.run(query, parameters)

            products = []

            for record in result:
                product = record["p"]

                products.append(dict(product))

            return products

    def close(self):
        self.driver.close()