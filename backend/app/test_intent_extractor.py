from backend.app.agent.intent_extractor import extract_intent


query = "I want earbuds under 3000 rupees with noise cancellation and at least 30 hours of battery."

intent = extract_intent(query)

print(intent)
print()
print("CATEGORY:", intent.category)
print("MAX PRICE:", intent.max_price)
print("NOISE CANCELLATION:", intent.noise_cancellation)
print("MIN BATTERY:", intent.min_battery_hours)