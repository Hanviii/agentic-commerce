from backend.app.neo4j_client import Neo4jClient

client = Neo4jClient()

try:
    query = """
    MATCH (p:Product)
    WHERE p.category = "Keyboard"
    RETURN p
    ORDER BY p.rating DESC
    """

    products = client.execute_query(query, {})

    print("\nKEYBOARD PRODUCTS:\n")

    for product in products:
        print(
            f"{product['name']} | "
            f"₹{product['price']} | "
            f"Type: {product['keyboard_type']} | "
            f"Wireless: {product['wireless']} | "
            f"RGB: {product['rgb']} | "
            f"Hot-swappable: {product['hot_swappable']} | "
            f"Layout: {product['layout']} | "
            f"Rating: {product['rating']}"
        )

finally:
    client.close()