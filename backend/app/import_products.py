import csv
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

URI = URI.replace("neo4j+s://", "neo4j+ssc://")

CSV_PATH = "data/products.csv"
MERCHANT_NAME = "AgentCart Store"


def import_products():
    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:
        with driver.session() as session:
            with open(CSV_PATH, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                for product in reader:
                    session.run(
                        """
                        MERGE (p:Product {id: $id})
                        SET p.name = $name,
                            p.brand = $brand,
                            p.category = $category,
                            p.price = toFloat($price),
                            p.rating = toFloat($rating),
                            p.stock = toInteger($stock),
                            p.description = $description,
                            p.battery_hours = CASE
                                WHEN $battery_hours = '' THEN null
                                ELSE toFloat($battery_hours)
                            END,
                            p.battery_days = CASE
                                WHEN $battery_days = '' THEN null
                                ELSE toFloat($battery_days)
                            END,
                            p.noise_cancellation = CASE
                                WHEN $noise_cancellation = '' THEN null
                                ELSE toBoolean($noise_cancellation)
                            END,
                            p.water_resistance = $water_resistance,
                            p.connectivity = $connectivity,
                            p.microphone_count = CASE
                                WHEN $microphone_count = '' THEN null
                                ELSE toInteger($microphone_count)
                            END,
                            p.charging_type = $charging_type,
                            p.weight_grams = CASE
                                WHEN $weight_grams = '' THEN null
                                ELSE toFloat($weight_grams)
                            END,
                            p.fast_charging = CASE
                                WHEN $fast_charging = '' THEN null
                                ELSE toBoolean($fast_charging)
                            END,
                            p.spatial_audio = CASE
                                WHEN $spatial_audio = '' THEN null
                                ELSE toBoolean($spatial_audio)
                            END,
                            p.gps = CASE
                                WHEN $gps = '' THEN null
                                ELSE toBoolean($gps)
                            END,
                            p.display_type = $display_type,
                            p.display_size_inches = CASE
                                WHEN $display_size_inches = '' THEN null
                                ELSE toFloat($display_size_inches)
                            END,
                            p.heart_rate_monitor = CASE
                                WHEN $heart_rate_monitor = '' THEN null
                                ELSE toBoolean($heart_rate_monitor)
                            END,
                            p.spo2_monitor = CASE
                                WHEN $spo2_monitor = '' THEN null
                                ELSE toBoolean($spo2_monitor)
                            END,
                            p.sleep_tracking = CASE
                                WHEN $sleep_tracking = '' THEN null
                                ELSE toBoolean($sleep_tracking)
                            END,
                            p.step_tracking = CASE
                                WHEN $step_tracking = '' THEN null
                                ELSE toBoolean($step_tracking)
                            END,
                            p.calling = CASE
                                WHEN $calling = '' THEN null
                                ELSE toBoolean($calling)
                            END,
                            p.layout = $layout,
                            p.keyboard_type = $keyboard_type,
                            p.wireless = CASE
                                WHEN $wireless = '' THEN null
                                ELSE toBoolean($wireless)
                            END,
                            p.switch_type = $switch_type,
                            p.backlit = CASE
                                WHEN $backlit = '' THEN null
                                ELSE toBoolean($backlit)
                            END,
                            p.rgb = CASE
                                WHEN $rgb = '' THEN null
                                ELSE toBoolean($rgb)
                            END,
                            p.hot_swappable = CASE
                                WHEN $hot_swappable = '' THEN null
                                ELSE toBoolean($hot_swappable)
                            END,
                            p.key_count = CASE
                                WHEN $key_count = '' THEN null
                                ELSE toInteger($key_count)
                            END

                        MERGE (b:Brand {name: $brand})
                        MERGE (c:Category {name: $category})
                        MERGE (m:Merchant {name: $merchant})

                        MERGE (p)-[:MADE_BY]->(b)
                        MERGE (p)-[:BELONGS_TO]->(c)
                        MERGE (m)-[:SELLS]->(p)
                        """,
                        **product,
                        merchant=MERCHANT_NAME
                    )

        print("Products imported successfully.")

    finally:
        driver.close()


if __name__ == "__main__":
    import_products()