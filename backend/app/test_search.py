from backend.app.search import search_from_query


user_query = (
    "I want earbuds under 3000 rupees "
    "with noise cancellation and at least 30 hours of battery."
)

products = search_from_query(user_query)

print("\nMATCHING PRODUCTS:\n")

for product in products:
    print(
        f"{product['name']} | "
        f"₹{product['price']} | "
        f"Rating: {product['rating']} | "
        f"Battery: {product['battery_hours']}h"
    )