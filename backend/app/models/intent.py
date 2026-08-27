from typing import Optional, Literal

from pydantic import BaseModel, Field


class ShoppingIntent(BaseModel):
    """
    Structured representation of what the user wants to buy.
    """

    category: Optional[Literal[
        "Earbuds",
        "Smartwatch",
        "Keyboard"
    ]] = None

    min_price: Optional[float] = Field(default=None, ge=0)
    max_price: Optional[float] = Field(default=None, ge=0)

    min_rating: Optional[float] = Field(
        default=None,
        ge=0,
        le=5
    )

    brand: Optional[str] = None

    # Earbuds
    min_battery_hours: Optional[float] = Field(default=None, ge=0)
    noise_cancellation: Optional[bool] = None
    spatial_audio: Optional[bool] = None

    # Smartwatch
    min_battery_days: Optional[float] = Field(default=None, ge=0)
    gps: Optional[bool] = None
    calling: Optional[bool] = None

    # Keyboard
    keyboard_type: Optional[str] = None
    wireless: Optional[bool] = None
    rgb: Optional[bool] = None
    hot_swappable: Optional[bool] = None
    layout: Optional[str] = None

    # How results should be ranked
    sort_by: Optional[Literal[
        "rating",
        "price_low",
        "price_high",
        "battery"
    ]] = "rating"