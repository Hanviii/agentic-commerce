from backend.app.models.intent import ShoppingIntent
from backend.app.agent.cypher_generator import generate_cypher
from backend.app.neo4j_client import Neo4jClient



def search_products(intent: ShoppingIntent):

    # Step 1: Convert intent into Cypher
    query, parameters = generate_cypher(intent)

    # Step 2: Execute Cypher against Neo4j
    client = Neo4jClient()

    try:
        products = client.execute_query(query, parameters)
    finally:
        client.close()

    return products