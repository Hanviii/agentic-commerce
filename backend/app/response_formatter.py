def format_product(product: dict) -> dict:
    """
    Convert a raw Neo4j product dictionary into
    a clean product response.
    """

    return {
        "id": product.get("id"),
        "name": product.get("name"),
        "brand": product.get("brand"),
        "category": product.get("category"),
        "price": product.get("price"),
        "rating": product.get("rating"),
        "description": product.get("description"),
        "stock": product.get("stock"),

        # Common product attributes
        "battery_hours": product.get("battery_hours"),
        "battery_days": product.get("battery_days"),

        # Earbuds
        "noise_cancellation": product.get("noise_cancellation"),
        "spatial_audio": product.get("spatial_audio"),

        # Smartwatch
        "gps": product.get("gps"),
        "calling": product.get("calling"),

        # Keyboard
        "keyboard_type": product.get("keyboard_type"),
        "wireless": product.get("wireless"),
        "rgb": product.get("rgb"),
        "hot_swappable": product.get("hot_swappable"),
        "layout": product.get("layout"),
    }


def format_products(products: list[dict]) -> list[dict]:
    """
    Format a list of raw Neo4j products.
    """

    return [
        format_product(product)
        for product in products
    ]