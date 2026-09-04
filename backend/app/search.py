from backend.app.response_formatter import format_products

from backend.app.models.search_response import SearchResponse
from backend.app.models.intent import ShoppingIntent

from backend.app.agent.intent_extractor import extract_intent
from backend.app.agent.cypher_generator import generate_cypher
from backend.app.agent.recommendation_agent import (
    generate_recommendation,
    rank_products,
)

from backend.app.neo4j_client import Neo4jClient


def search_products(intent: ShoppingIntent):
    """
    Search Neo4j using an already extracted ShoppingIntent.
    """

    # ---------------------------------------------------------
    # STEP 1: Convert intent into Cypher
    # ---------------------------------------------------------

    query, parameters = generate_cypher(intent)

    # ---------------------------------------------------------
    # STEP 2: Execute Cypher against Neo4j
    # ---------------------------------------------------------

    client = Neo4jClient()

    try:
        products = client.execute_query(query, parameters)
    finally:
        client.close()

    return products


def search_from_query(user_query: str):
    """
    Complete shopping search pipeline.

    Natural language
        -> LLM intent extraction
        -> ShoppingIntent
        -> Cypher
        -> Neo4j
        -> formatted products
        -> deterministic ranking
        -> LLM recommendations
        -> structured search response
    """

    # ---------------------------------------------------------
    # STEP 1: Extract structured intent
    # ---------------------------------------------------------

    intent = extract_intent(user_query)

    print("\nEXTRACTED INTENT:")
    print(intent)

    # ---------------------------------------------------------
    # STEP 2: Search Neo4j
    # ---------------------------------------------------------

    products = search_products(intent)

    # ---------------------------------------------------------
    # STEP 3: Format products
    # ---------------------------------------------------------

    formatted_products = format_products(products)

    # ---------------------------------------------------------
    # STEP 4: Deterministically rank products
    # ---------------------------------------------------------

    ranked_products = rank_products(
        intent=intent,
        products=formatted_products,
    )

    # ---------------------------------------------------------
    # STEP 5: Generate recommendations
    # ---------------------------------------------------------

    recommendation = generate_recommendation(
        user_query=user_query,
        intent=intent,
        products=ranked_products,
    )

    # ---------------------------------------------------------
    # STEP 6: Build final structured response
    # ---------------------------------------------------------

    return SearchResponse(
        query=user_query,
        intent=intent.model_dump(),
        count=len(ranked_products),
        sort_by=intent.sort_by,
        products=ranked_products,
        recommendations=recommendation,
    )