from backend.app.models.intent import ShoppingIntent
from backend.app.search import search_products


intent = ShoppingIntent(
    category="Earbuds",
    max_price=3000,
    min_battery_hours=30,
    noise_cancellation=True,
    sort_by="rating"
)

products = search_products(intent)

print("\nMATCHING PRODUCTS:\n")

for product in products:
    print(
        f"{product['name']} | "
        f"₹{product['price']} | "
        f"Rating: {product['rating']} | "
        f"Battery: {product['battery_hours']}h"
    )