from backend.app.models.intent import ShoppingIntent


def generate_cypher(intent: ShoppingIntent):
    """
    Convert a validated ShoppingIntent into a safe Cypher query.
    """

    conditions = []
    parameters = {}

    # -------------------------
    # Category
    # -------------------------
    if intent.category:
        conditions.append("p.category = $category")
        parameters["category"] = intent.category

    # -------------------------
    # Price
    # -------------------------
    if intent.min_price is not None:
        conditions.append("p.price >= $min_price")
        parameters["min_price"] = intent.min_price

    if intent.max_price is not None:
        conditions.append("p.price <= $max_price")
        parameters["max_price"] = intent.max_price

    # -------------------------
    # Rating
    # -------------------------
    if intent.min_rating is not None:
        conditions.append("p.rating >= $min_rating")
        parameters["min_rating"] = intent.min_rating

    # -------------------------
    # Brand
    # -------------------------
    if intent.brand:
        conditions.append("p.brand = $brand")
        parameters["brand"] = intent.brand

    # -------------------------
    # Earbuds
    # -------------------------
    if intent.min_battery_hours is not None:
        conditions.append("p.battery_hours >= $min_battery_hours")
        parameters["min_battery_hours"] = intent.min_battery_hours

    if intent.noise_cancellation is not None:
        conditions.append("p.noise_cancellation = $noise_cancellation")
        parameters["noise_cancellation"] = intent.noise_cancellation

    if intent.spatial_audio is not None:
        conditions.append("p.spatial_audio = $spatial_audio")
        parameters["spatial_audio"] = intent.spatial_audio

    # -------------------------
    # Smartwatch
    # -------------------------
    if intent.min_battery_days is not None:
        conditions.append("p.battery_days >= $min_battery_days")
        parameters["min_battery_days"] = intent.min_battery_days

    if intent.gps is not None:
        conditions.append("p.gps = $gps")
        parameters["gps"] = intent.gps

    if intent.calling is not None:
        conditions.append("p.calling = $calling")
        parameters["calling"] = intent.calling

    # -------------------------
    # Keyboard
    # -------------------------
    if intent.keyboard_type:
        conditions.append("p.keyboard_type = $keyboard_type")
        parameters["keyboard_type"] = intent.keyboard_type

    if intent.wireless is not None:
        conditions.append("p.wireless = $wireless")
        parameters["wireless"] = intent.wireless

    if intent.rgb is not None:
        conditions.append("p.rgb = $rgb")
        parameters["rgb"] = intent.rgb

    if intent.hot_swappable is not None:
        conditions.append("p.hot_swappable = $hot_swappable")
        parameters["hot_swappable"] = intent.hot_swappable

    if intent.layout:
        conditions.append("p.layout = $layout")
        parameters["layout"] = intent.layout

    # -------------------------
    # WHERE clause
    # -------------------------
    where_clause = ""

    if conditions:
        where_clause = "WHERE " + "\n  AND ".join(conditions)

    # -------------------------
    # Sorting
    # -------------------------
    if intent.sort_by == "price_low":
        sort_expression = "p.price ASC"

    elif intent.sort_by == "price_high":
        sort_expression = "p.price DESC"

    elif intent.sort_by == "battery":
        if intent.category == "Smartwatch":
            sort_expression = "p.battery_days DESC"
        else:
            sort_expression = "p.battery_hours DESC"

    else:
        sort_expression = "p.rating DESC"

    # -------------------------
    # Final query
    # -------------------------
    query = f"""
    MATCH (p:Product)
    {where_clause}
    RETURN p
    ORDER BY {sort_expression}
    LIMIT 10
    """

    return query, parameters