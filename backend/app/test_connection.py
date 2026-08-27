import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv("backend/.env")

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Use neo4j+ssc for the current local Python certificate issue
URI = URI.replace("neo4j+s://", "neo4j+ssc://")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

try:
    with driver.session() as session:
        result = session.run(
            'RETURN "Python → Neo4j connection successful!" AS message'
        )
        print(result.single()["message"])

finally:
    driver.close()