from typing import Any

from pydantic import BaseModel

from backend.app.models.recommendation import RecommendationResponse


class SearchResponse(BaseModel):
    """
    Structured response returned by the complete
    shopping search and recommendation pipeline.
    """

    query: str
    intent: dict[str, Any]
    count: int
    sort_by: str
    products: list[dict[str, Any]]
    recommendations: RecommendationResponse