import json

from ollama import chat

from backend.app.models.intent import ShoppingIntent
from backend.app.models.recommendation import (
    ProductRecommendation,
    RecommendationResponse,
)


def rank_products(
    intent: ShoppingIntent,
    products: list[dict],
) -> list[dict]:
    """
    Deterministically rank already-filtered products.

    Filtering is handled by Neo4j.
    Ranking is handled here.
    The LLM does not decide ranking.
    """

    if not products:
        return []

    # ---------------------------------------------------------
    # PRICE: LOWEST FIRST
    # ---------------------------------------------------------

    if intent.sort_by == "price_low":
        return sorted(
            products,
            key=lambda p: (
                float(p.get("price"))
                if p.get("price") is not None
                else float("inf")
            ),
        )

    # ---------------------------------------------------------
    # PRICE: HIGHEST FIRST
    # ---------------------------------------------------------

    if intent.sort_by == "price_high":
        return sorted(
            products,
            key=lambda p: (
                float(p.get("price"))
                if p.get("price") is not None
                else float("-inf")
            ),
            reverse=True,
        )

    # ---------------------------------------------------------
    # BATTERY
    # ---------------------------------------------------------

    if intent.sort_by == "battery":

        if intent.category == "Smartwatch":
            return sorted(
                products,
                key=lambda p: (
                    float(p.get("battery_days"))
                    if p.get("battery_days") is not None
                    else float("-inf")
                ),
                reverse=True,
            )

        return sorted(
            products,
            key=lambda p: (
                float(p.get("battery_hours"))
                if p.get("battery_hours") is not None
                else float("-inf")
            ),
            reverse=True,
        )

    # ---------------------------------------------------------
    # DEFAULT: HIGHEST RATING
    # ---------------------------------------------------------

    return sorted(
        products,
        key=lambda p: (
            float(p.get("rating"))
            if p.get("rating") is not None
            else float("-inf")
        ),
        reverse=True,
    )


def build_candidate_facts(
    intent: ShoppingIntent,
    candidates: list[dict],
) -> list[dict]:
    """
    Build a small factual representation for the LLM.

    This deliberately contains only facts that the LLM
    is allowed to mention.
    """

    facts = []

    for product in candidates:

        product_facts = {
            "product_id": product.get("id"),
            "name": product.get("name"),
            "brand": product.get("brand"),
            "price": product.get("price"),
            "rating": product.get("rating"),
        }

        # ---------------------------------------------------------
        # KEYBOARD FACTS
        # ---------------------------------------------------------

        if intent.category == "Keyboard":

            product_facts.update({
                "keyboard_type": product.get("keyboard_type"),
                "wireless": product.get("wireless"),
                "rgb": product.get("rgb"),
                "hot_swappable": product.get("hot_swappable"),
                "layout": product.get("layout"),
            })

        # ---------------------------------------------------------
        # EARBUD FACTS
        # ---------------------------------------------------------

        elif intent.category == "Earbuds":

            product_facts.update({
                "battery_hours": product.get("battery_hours"),
                "noise_cancellation": product.get(
                    "noise_cancellation"
                ),
                "spatial_audio": product.get(
                    "spatial_audio"
                ),
            })

        # ---------------------------------------------------------
        # SMARTWATCH FACTS
        # ---------------------------------------------------------

        elif intent.category == "Smartwatch":

            product_facts.update({
                "battery_days": product.get("battery_days"),
                "gps": product.get("gps"),
                "calling": product.get("calling"),
            })

        facts.append(product_facts)

    return facts

def build_deterministic_recommendations(
    intent: ShoppingIntent,
    ranked_products: list[dict],
) -> list[ProductRecommendation]:
    """
    Generate factual recommendation reasons deterministically.

    The LLM is not used for product-specific claims.
    """

    candidates = ranked_products[:3]

    if not candidates:
        return []

    recommendations = []

    for index, product in enumerate(candidates):

        product_id = product.get("id")
        name = product.get("name")

        if not product_id:
            continue

        # ---------------------------------------------------------
        # SMARTWATCH
        # ---------------------------------------------------------

        if intent.category == "Smartwatch":

            battery = product.get("battery_days")
            gps = product.get("gps")

            if intent.sort_by == "battery" and battery is not None:

                if index == 0:
                    reason = (
                        f"{name} offers the longest battery life "
                        f"at {battery:g} days."
                    )
                elif index == 1:
                    reason = (
                        f"{name} offers {battery:g} days of battery life, "
                        f"second among the selected products."
                    )
                else:
                    reason = (
                        f"{name} offers {battery:g} days of battery life."
                    )

            else:
                details = []

                if gps is True:
                    details.append("GPS")

                if product.get("calling") is True:
                    details.append("calling")

                if battery is not None:
                    details.append(
                        f"{battery:g} days of battery life"
                    )

                if details:
                    reason = (
                        f"{name} supports "
                        + ", ".join(details)
                        + "."
                    )
                else:
                    reason = f"{name} matches the requested criteria."

        # ---------------------------------------------------------
        # EARBUDS
        # ---------------------------------------------------------

        elif intent.category == "Earbuds":

            battery = product.get("battery_hours")
            details = []

            if product.get("noise_cancellation") is True:
                details.append("ANC")

            if product.get("spatial_audio") is True:
                details.append("spatial audio")

            if battery is not None:
                details.append(
                    f"{battery:g} hours of battery life"
                )

            if details:
                reason = (
                    f"{name} offers "
                    + ", ".join(details)
                    + "."
                )
            else:
                reason = f"{name} matches the requested criteria."

        # ---------------------------------------------------------
        # KEYBOARD
        # ---------------------------------------------------------

        elif intent.category == "Keyboard":

            details = []

            if product.get("keyboard_type"):
                details.append(product["keyboard_type"])

            if product.get("wireless") is True:
                details.append("wireless")

            if product.get("rgb") is True:
                details.append("RGB")

            if product.get("hot_swappable") is True:
                details.append("hot-swappable")

            if product.get("layout"):
                details.append(product["layout"])

            if details:
                reason = (
                    f"{name} is a "
                    + ", ".join(details)
                    + " keyboard."
                )
            else:
                reason = f"{name} matches the requested criteria."

        else:
            reason = f"{name} matches the requested criteria."

        recommendations.append(
            ProductRecommendation(
                product_id=product_id,
                reason=reason,
            )
        )

    return recommendations

def generate_recommendation(
    user_query: str,
    intent: ShoppingIntent,
    products: list[dict],
) -> RecommendationResponse:
    """
    Generate grounded product recommendations.

    Ranking is deterministic.
    The LLM only converts supplied facts into concise explanations.
    """

    # ---------------------------------------------------------
    # NO RESULTS
    # ---------------------------------------------------------

    if not products:

        return RecommendationResponse(
            summary=(
                "I couldn't find any products matching "
                "your requirements."
            ),
            recommendations=[],
        )

    # ---------------------------------------------------------
    # STEP 1: DETERMINISTIC RANKING
    # ---------------------------------------------------------

    ranked_products = rank_products(
        intent=intent,
        products=products,
    )

    # Only send the strongest 3 candidates to the LLM.
    candidates = ranked_products[:3]

    # ---------------------------------------------------------
    # STEP 2: BUILD FACTS
    # ---------------------------------------------------------

    candidate_facts = build_candidate_facts(
        intent=intent,
        candidates=candidates,
    )

    product_data = json.dumps(
        candidate_facts,
        indent=2,
    )

    valid_product_ids = {
        product["product_id"]
        for product in candidate_facts
        if product.get("product_id") is not None
    }

    # ---------------------------------------------------------
    # STEP 3: LLM EXPLANATION
    # ---------------------------------------------------------

    prompt = f"""
You are a product recommendation explanation assistant.

USER QUERY:
{user_query}

SHOPPING INTENT:
{intent.model_dump_json(indent=2)}

PRODUCT FACTS:
{product_data}

The application has already selected these products.

Your ONLY job is to explain why these products are relevant.

IMPORTANT:

The PRODUCT FACTS are the ONLY source of truth.

Never use outside knowledge.

Never guess.

Never infer an unsupported specification.

Never change a number.

Never change a currency.

Never claim a product is outside the budget
if its supplied price is within the supplied maximum price.

Never claim a product is within the budget
if its supplied price exceeds the supplied maximum price.

Never mention a feature unless that feature exists
in PRODUCT FACTS.

Never invent a comparison.

Never call something "best" unless the supplied data
clearly supports that wording.

Return at most 3 recommendations.

Each recommendation must use an EXACT product_id
from PRODUCT FACTS.

Do not repeat product IDs.

Each reason must be ONE concise sentence.

The reason should directly connect the product facts
to the user's actual requirements.

IMPORTANT DISTINCTION:

A user preference such as "longest battery life",
"cheapest", "most expensive", or "highest rated"
is a REQUEST TO RANK PRODUCTS.

It is NOT a minimum or maximum requirement.

For example:

User says "longest battery life":
- Do NOT say "at least 15 days" unless the user explicitly
  requested at least 15 days.
- Instead, say that the product has 15 days of battery life
  or that it has the longest battery life among the selected
  products.

User says "cheapest":
- Do NOT invent a maximum or minimum price requirement.
- Explain the actual price and that it is the lowest-priced
  selected product when supported by the supplied facts.

User says "highest rated":
- Do NOT invent a minimum rating.
- Explain the actual rating and that it is among the
  highest-rated selected products when supported by the
  supplied facts.

Never convert a ranking preference into a numeric requirement.

If the user requested a price limit, mention the actual
price when useful.

If the user requested a specific feature, mention that
feature when it is present in PRODUCT FACTS.

If the user requested a ranking criterion such as longest
battery life, cheapest, most expensive, or highest rated,
describe the actual ranking rather than inventing a
threshold.

Return ONLY valid JSON.

OUTPUT FORMAT:

{{
  "summary": "One concise factual summary.",
  "recommendations": [
    {{
      "product_id": "EXACT_PRODUCT_ID",
      "reason": "One concise factual explanation."
    }}
  ]
}}
"""

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

    print("\nRAW RECOMMENDATION RESPONSE:")
    print(response.message.content)

    # ---------------------------------------------------------
    # STEP 4: PARSE JSON
    # ---------------------------------------------------------

    try:

        data = json.loads(
            response.message.content
        )

    except json.JSONDecodeError:

        return RecommendationResponse(
            summary=(
                "I found matching products, but couldn't "
                "generate recommendations."
            ),
            recommendations=[],
        )

    # ---------------------------------------------------------
    # STEP 5: VALIDATE RECOMMENDATIONS
    # ---------------------------------------------------------

    recommendations = []
    seen_product_ids = set()

    for recommendation in data.get(
        "recommendations",
        [],
    ):

        product_id = recommendation.get(
            "product_id"
        )

        # Product must be one of our candidates.
        if product_id not in valid_product_ids:
            continue

        # Prevent duplicates.
        if product_id in seen_product_ids:
            continue

        reason = str(
            recommendation.get(
                "reason",
                "",
            )
        ).strip()

        # Don't return empty explanations.
        if not reason:
            continue

        seen_product_ids.add(product_id)

        recommendations.append(
            ProductRecommendation(
                product_id=product_id,
                reason=reason,
            )
        )

        if len(recommendations) == 3:
            break

    # ---------------------------------------------------------
    # STEP 6: SUMMARY
    # ---------------------------------------------------------

    summary = str(
        data.get(
            "summary",
            "",
        )
    ).strip()

    if not summary:

        summary = (
            f"I found {len(products)} products "
            "matching your requirements."
        )

    # ---------------------------------------------------------
    # FINAL RESPONSE
    # ---------------------------------------------------------

    return RecommendationResponse(
        summary=summary,
        recommendations=recommendations,
    )