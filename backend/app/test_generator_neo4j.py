from backend.app.models.intent import ShoppingIntent
from backend.app.agent.cypher_generator import generate_cypher
from backend.app.database import driver


intent = ShoppingIntent(
    category="Earbuds",
    max_price=3000,
    min_battery_hours=30,
    noise_cancellation=True
)

query, parameters = generate_cypher(intent)

print("Generated query:")
print(query)

print("\nParameters:")
print(parameters)

with driver.session() as session:
    result = session.run(query, parameters)

    print("\nProducts found:")

    for record in result:
        product = record["p"]
        print(
            product["name"],
            "| ₹", product["price"],
            "| Rating:", product["rating"]
        )