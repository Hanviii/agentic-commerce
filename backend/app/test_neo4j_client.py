from backend.app.neo4j_client import Neo4jClient


client = Neo4jClient()

try:
    query = """
    MATCH (p:Product)
    RETURN p
    LIMIT 5
    """

    products = client.execute_query(query, {})

    for product in products:
        print(product)

finally:
    client.close()