from backend.app.models.intent import ShoppingIntent
from backend.app.agent.cypher_generator import generate_cypher


intent = ShoppingIntent(
    category="Earbuds",
    max_price=3000,
    min_battery_hours=30,
    noise_cancellation=True
)

query, parameters = generate_cypher(intent)

print("QUERY:")
print(query)

print("PARAMETERS:")
print(parameters)