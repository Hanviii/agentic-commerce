from typing import List

from pydantic import BaseModel, Field


class ProductRecommendation(BaseModel):
    product_id: str
    reason: str = Field(min_length=1)


class RecommendationResponse(BaseModel):
    summary: str
    recommendations: List[ProductRecommendation] = Field(default_factory=list)