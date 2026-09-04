import json
import re

from ollama import chat

from backend.app.models.intent import ShoppingIntent


def extract_intent(user_query: str) -> ShoppingIntent:
    """
    Convert a natural-language shopping request into ShoppingIntent
    using the local Llama model.
    """

    prompt = f"""
You are an information extraction system.

Your ONLY job is to extract shopping requirements from the user's sentence.

You MUST return valid JSON.

The JSON fields are:

category
min_price
max_price
min_rating
brand
min_battery_hours
noise_cancellation
spatial_audio
min_battery_days
gps
calling
keyboard_type
wireless
rgb
hot_swappable
layout
sort_by

IMPORTANT RULES:

CATEGORY:
- If the user says "earbuds", category MUST be "Earbuds".
- If the user says "smartwatch" or "smart watch", category MUST be "Smartwatch".
- If the user says "keyboard" or "keyboards", category MUST be "Keyboard".
- If the category cannot be determined, use null.

PRICE:
- "under ₹3000" means min_price = null and max_price = 3000.
- "below ₹3000" means min_price = null and max_price = 3000.
- "less than ₹3000" means min_price = null and max_price = 3000.
- "up to ₹3000" means min_price = null and max_price = 3000.
- "above ₹3000" means min_price = 3000 and max_price = null.
- "over ₹3000" means min_price = 3000 and max_price = null.
- "more than ₹3000" means min_price = 3000 and max_price = null.
- If the user gives only an upper price limit, NEVER set min_price.
- If the user gives only a lower price limit, NEVER set max_price.

RATING:
- min_rating MUST ALWAYS be a number such as 4.0 or 4.5, or null.
- NEVER put words or phrases into min_rating.
- "highly rated" means sort_by = "rating" and min_rating = null.
- "top rated" means sort_by = "rating" and min_rating = null.
- "best rated" means sort_by = "rating" and min_rating = null.
- "highest rated" means sort_by = "rating" and min_rating = null.
- "rated 4.5 and above" means min_rating = 4.5.
- "4 stars or above" means min_rating = 4.0.
- "rating above 4" means min_rating = 4.0.

BATTERY:
- "at least 30 hours" means min_battery_hours = 30.
- "30 hours or more" means min_battery_hours = 30.
- "at least 5 days" means min_battery_days = 5.
- "5 days or more" means min_battery_days = 5.

EARBUD FEATURES:
- "with noise cancellation" means noise_cancellation = true.
- "with ANC" means noise_cancellation = true.
- "ANC" means noise_cancellation = true.
- "without noise cancellation" means noise_cancellation = false.
- "without ANC" means noise_cancellation = false.
- "with spatial audio" means spatial_audio = true.
- "without spatial audio" means spatial_audio = false.

SMARTWATCH FEATURES:
- "with GPS" means gps = true.
- "without GPS" means gps = false.
- "with calling" means calling = true.
- "without calling" means calling = false.

KEYBOARD FEATURES:
- "mechanical keyboard" means keyboard_type = "Mechanical".
- "membrane keyboard" means keyboard_type = "Membrane".
- "wireless keyboard" means wireless = true.
- "wired keyboard" means wireless = false.
- "keyboard with RGB" means rgb = true.
- "RGB keyboard" means rgb = true.
- "without RGB" means rgb = false.
- "hot-swappable keyboard" means hot_swappable = true.
- "hot swappable keyboard" means hot_swappable = true.
- "not hot-swappable" means hot_swappable = false.
- "TKL keyboard" means layout = "TKL".
- "75% keyboard" means layout = "75%".
- "60% keyboard" means layout = "60%".
- "full-size keyboard" means layout = "Full-size".

IMPORTANT KEYBOARD RULE:
- "wireless" describes the wireless field, NOT keyboard_type.
- keyboard_type can ONLY be "Mechanical", "Membrane", or null.
- NEVER set keyboard_type to "Wireless".

PAYMENT METHOD:
If the user explicitly mentions a preferred payment method, extract it into payment_method.

Examples:
"buy earbuds via Navi UPI" -> payment_method = "Navi UPI"
"pay using UPI" -> payment_method = "UPI"
"checkout with Google Pay" -> payment_method = "Google Pay"
"pay through credit card" -> payment_method = "Credit Card"

If no payment method is mentioned, payment_method = null.

Do not invent a payment method.

SORTING:

ONLY set sort_by = "price_low" if the user explicitly asks for:
- cheapest
- lowest price
- least expensive
- most affordable

ONLY set sort_by = "price_high" if the user explicitly asks for:
- most expensive
- highest price
- costliest

ONLY set sort_by = "rating" if the user explicitly asks for:
- highly rated
- top rated
- best rated
- highest rated

CRITICAL:
A price constraint such as "under ₹3000", "below ₹3000",
"less than ₹3000", "above ₹3000", or "over ₹3000"
does NOT mean the user wants products sorted by price.

If the user does not explicitly request sorting,
ALWAYS set sort_by = "rating".

Examples:

"wireless keyboards under ₹3000"
-> sort_by = "rating"

"cheapest wireless keyboards under ₹3000"
-> sort_by = "price_low"

"most expensive wireless keyboards"
-> sort_by = "price_high"

"best rated wireless keyboards under ₹3000"
-> sort_by = "rating"

GENERAL:
- If the user does NOT mention a field, use null.
- Do NOT invent products.
- Do NOT invent brands.
- Do NOT recommend anything.
- Return ONLY JSON.
- Do not include explanations.
- Do not use markdown.
- Boolean fields must contain only true, false, or null.
- Numeric fields must contain only numbers or null.

Example 1:

User:
I want earbuds under 3000 rupees with noise cancellation and at least 30 hours of battery.

Correct JSON:
{{
  "category": "Earbuds",
  "min_price": null,
  "max_price": 3000,
  "min_rating": null,
  "brand": null,
  "min_battery_hours": 30,
  "noise_cancellation": true,
  "spatial_audio": null,
  "min_battery_days": null,
  "gps": null,
  "calling": null,
  "keyboard_type": null,
  "wireless": null,
  "rgb": null,
  "hot_swappable": null,
  "layout": null,
  "sort_by": "rating"
}}

Example 2:

User:
Find highly rated wireless keyboards.

Correct JSON:
{{
  "category": "Keyboard",
  "min_price": null,
  "max_price": null,
  "min_rating": null,
  "brand": null,
  "min_battery_hours": null,
  "noise_cancellation": null,
  "spatial_audio": null,
  "min_battery_days": null,
  "gps": null,
  "calling": null,
  "keyboard_type": null,
  "wireless": true,
  "rgb": null,
  "hot_swappable": null,
  "layout": null,
  "sort_by": "rating"
}}

Example 3:

User:
Show me wireless mechanical keyboards with RGB under ₹3000.

Correct JSON:
{{
  "category": "Keyboard",
  "min_price": null,
  "max_price": 3000,
  "min_rating": null,
  "brand": null,
  "min_battery_hours": null,
  "noise_cancellation": null,
  "spatial_audio": null,
  "min_battery_days": null,
  "gps": null,
  "calling": null,
  "keyboard_type": "Mechanical",
  "wireless": true,
  "rgb": true,
  "hot_swappable": null,
  "layout": null,
  "sort_by": "rating"
}}

Example 4:

User:
Find smartwatches under ₹5000 with GPS.

Correct JSON:
{{
  "category": "Smartwatch",
  "min_price": null,
  "max_price": 5000,
  "min_rating": null,
  "brand": null,
  "min_battery_hours": null,
  "noise_cancellation": null,
  "spatial_audio": null,
  "min_battery_days": null,
  "gps": true,
  "calling": null,
  "keyboard_type": null,
  "wireless": null,
  "rgb": null,
  "hot_swappable": null,
  "layout": null,
  "sort_by": "rating"
}}

Now extract the requirements from this user request:

{user_query}
"""

    # ---------------------------------------------------------
    # STEP 1: ASK LLAMA TO EXTRACT INTENT
    # ---------------------------------------------------------

    response = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format="json",
    )

    print("\nRAW LLM RESPONSE:")
    print(response.message.content)

    # ---------------------------------------------------------
    # STEP 2: PARSE JSON
    # ---------------------------------------------------------

    data = json.loads(response.message.content)

    # ---------------------------------------------------------
    # STEP 3: NORMALIZATION
    # ---------------------------------------------------------

    # min_rating must be numeric or null.
    if not isinstance(data.get("min_rating"), (int, float)):
        data["min_rating"] = None

    # ---------------------------------------------------------
    # KEYBOARD TYPE
    # ---------------------------------------------------------

    keyboard_type = data.get("keyboard_type")

    if keyboard_type:
        keyboard_type = str(keyboard_type).strip().lower()

        if keyboard_type == "mechanical":
            data["keyboard_type"] = "Mechanical"

        elif keyboard_type == "membrane":
            data["keyboard_type"] = "Membrane"

        else:
            data["keyboard_type"] = None

    # ---------------------------------------------------------
    # NOISE CANCELLATION
    # ---------------------------------------------------------

    noise_cancellation = data.get("noise_cancellation")

    if isinstance(noise_cancellation, str):
        value = noise_cancellation.strip().lower()

        if value in {
            "anc",
            "true",
            "yes",
            "with anc",
            "with noise cancellation",
            "noise cancellation",
        }:
            data["noise_cancellation"] = True

        elif value in {
            "false",
            "no",
            "without anc",
            "without noise cancellation",
        }:
            data["noise_cancellation"] = False

        else:
            data["noise_cancellation"] = None

    # ---------------------------------------------------------
    # SPATIAL AUDIO
    # ---------------------------------------------------------

    spatial_audio = data.get("spatial_audio")

    if isinstance(spatial_audio, str):
        value = spatial_audio.strip().lower()

        if value in {
            "true",
            "yes",
            "spatial audio",
            "with spatial audio",
        }:
            data["spatial_audio"] = True

        elif value in {
            "false",
            "no",
            "without spatial audio",
        }:
            data["spatial_audio"] = False

        else:
            data["spatial_audio"] = None

    # ---------------------------------------------------------
    # WIRELESS
    # ---------------------------------------------------------

    wireless = data.get("wireless")

    if isinstance(wireless, str):
        value = wireless.strip().lower()

        if value in {"true", "yes", "wireless"}:
            data["wireless"] = True

        elif value in {"false", "no", "wired"}:
            data["wireless"] = False

        else:
            data["wireless"] = None

    # ---------------------------------------------------------
    # RGB
    # ---------------------------------------------------------

    rgb = data.get("rgb")

    if isinstance(rgb, str):
        value = rgb.strip().lower()

        if value in {"true", "yes", "rgb", "with rgb"}:
            data["rgb"] = True

        elif value in {"false", "no", "without rgb"}:
            data["rgb"] = False

        else:
            data["rgb"] = None

    # ---------------------------------------------------------
    # GPS
    # ---------------------------------------------------------

    gps = data.get("gps")

    if isinstance(gps, str):
        value = gps.strip().lower()

        if value in {"true", "yes", "gps", "with gps"}:
            data["gps"] = True

        elif value in {"false", "no", "without gps"}:
            data["gps"] = False

        else:
            data["gps"] = None

    # ---------------------------------------------------------
    # CALLING
    # ---------------------------------------------------------

    calling = data.get("calling")

    if isinstance(calling, str):
        value = calling.strip().lower()

        if value in {"true", "yes", "calling", "with calling"}:
            data["calling"] = True

        elif value in {"false", "no", "without calling"}:
            data["calling"] = False

        else:
            data["calling"] = None

    # ---------------------------------------------------------
    # CATEGORY
    # ---------------------------------------------------------

    query_lower = user_query.lower()

    if "earbud" in query_lower:
        data["category"] = "Earbuds"

    elif "smartwatch" in query_lower or "smart watch" in query_lower:
        data["category"] = "Smartwatch"

    elif "keyboard" in query_lower or "keyboards" in query_lower:
        data["category"] = "Keyboard"

    # ---------------------------------------------------------
    # DETERMINISTIC PRICE NORMALIZATION
    # ---------------------------------------------------------

    # "under", "below", "less than", "up to" => maximum price

    upper_price_match = re.search(
        r"(?:under|below|less than|up to)\s*[₹rs.]?\s*(\d+(?:\.\d+)?)",
        query_lower,
    )

    if upper_price_match:
        data["min_price"] = None
        data["max_price"] = float(upper_price_match.group(1))

    # "above", "over", "more than" => minimum price

    lower_price_match = re.search(
    r"(?:above|over|more than)\s*[₹rs.]?\s*(\d+(?:\.\d+)?)(?!\s*(?:star|stars|rating))",
    query_lower,
)

    if lower_price_match:
        data["min_price"] = float(lower_price_match.group(1))
        data["max_price"] = None

        # ---------------------------------------------------------
    # DETERMINISTIC PAYMENT METHOD NORMALIZATION
    # ---------------------------------------------------------

    # Detect explicit payment preferences from the user's query.
    # This is deterministic so payment preferences are not missed
    # by the LLM.

    payment_patterns = {
        "Navi UPI": [
            "navi upi",
            "navi",
        ],
        "BHIM UPI": [
            "bhim upi",
            "bhim",
        ],
        "Google Pay": [
            "google pay",
            "gpay",
        ],
        "PhonePe": [
            "phonepe",
            "phone pe",
        ],
        "Paytm": [
            "paytm",
        ],
    }

    for payment_method, patterns in payment_patterns.items():
        if any(pattern in query_lower for pattern in patterns):
            data["payment_method"] = payment_method
            break

        # ---------------------------------------------------------
    # DETERMINISTIC PRICE NORMALIZATION
    # ---------------------------------------------------------

    # "under", "below", "less than", "up to" => maximum price
    upper_price_match = re.search(
        r"(?:under|below|less than|up to)\s*[₹rs.]?\s*(\d+(?:\.\d+)?)",
        query_lower,
    )

    if upper_price_match:
        data["min_price"] = None
        data["max_price"] = float(upper_price_match.group(1))

    # "above", "over", "more than" => minimum price
    # Avoid confusing "above 4 star rating" with a price.
    lower_price_match = re.search(
        r"(?:above|over|more than)\s*[₹rs.]?\s*(\d+(?:\.\d+)?)(?!\s*(?:star|stars|rating))",
        query_lower,
    )

    if lower_price_match:
        data["min_price"] = float(lower_price_match.group(1))
        data["max_price"] = None

    # ---------------------------------------------------------
# KEYBOARD FEATURE NORMALIZATION
# ---------------------------------------------------------

# Only set layout when the user explicitly mentions it.
    if "tkl" in query_lower:
        data["layout"] = "TKL"

    elif "75%" in query_lower:
        data["layout"] = "75%"

    elif "60%" in query_lower:
        data["layout"] = "60%"

    elif "full-size" in query_lower or "full size" in   query_lower:
        data["layout"] = "Full-size"

    else:
        data["layout"] = None


# Only set keyboard type when explicitly mentioned.
    if "mechanical" in query_lower:
        data["keyboard_type"] = "Mechanical"

    elif "membrane" in query_lower:
        data["keyboard_type"] = "Membrane"

    else:
     data["keyboard_type"] = None


# Only set RGB when explicitly mentioned.
    if "without rgb" in query_lower:
        data["rgb"] = False

    elif "with rgb" in query_lower or "rgb" in query_lower:
        data["rgb"] = True

    else:
        data["rgb"] = None


# Only set hot-swappable when explicitly mentioned.
    if (
    "hot-swappable" in query_lower
    or "hot swappable" in query_lower
):
        data["hot_swappable"] = True

    elif (
    "not hot-swappable" in query_lower
    or "not hot swappable" in query_lower
    or "without hot-swappable" in query_lower
    or "without hot swappable" in query_lower
):
        data["hot_swappable"] = False

    else:
        data["hot_swappable"] = None

    # ---------------------------------------------------------
# SORTING
# ---------------------------------------------------------

    if (
    "highly rated" in query_lower
    or "top rated" in query_lower
    or "best rated" in query_lower
    or "highest rated" in query_lower
):
        data["sort_by"] = "rating"

    elif (
    "cheapest" in query_lower
    or "lowest price" in query_lower
    or "least expensive" in query_lower
    or "most affordable" in query_lower
):
        data["sort_by"] = "price_low"

    elif (
    "most expensive" in query_lower
    or "highest price" in query_lower
    or "costliest" in query_lower
):
        data["sort_by"] = "price_high"

    elif (
    "longest battery" in query_lower
    or "longest battery life" in query_lower
    or "best battery life" in query_lower
    or "maximum battery" in query_lower
    or "max battery" in query_lower
    or "most battery life" in query_lower
):
        data["sort_by"] = "battery"

    else:
    # Default sorting
        data["sort_by"] = "rating"

    # ---------------------------------------------------------
    # STEP 4: FINAL PYDANTIC VALIDATION
    # ---------------------------------------------------------

    intent = ShoppingIntent.model_validate(data)

    return intent