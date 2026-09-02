from fastapi import APIRouter, Body
from pydantic import BaseModel, Field
from typing import Optional, List
from services.market_compare_service import compare_market_prices

router = APIRouter(tags=["Market Comparison"])


class MarketCompareItem(BaseModel):
    market: str
    price: float
    trend: str  # UP | DOWN | STABLE
    distance: float
    distance_available: bool = True


class MarketCompareResponse(BaseModel):
    markets: List[MarketCompareItem]
    decision_summary: str
    data_source: str  # live | sample | fallback


class MarketCompareRequest(BaseModel):
    crop: str = Field(..., description="Crop name to compare across regional mandis")
    location: Optional[str] = Field("Vijayawada, Andhra Pradesh", description="Optional farmer location")


@router.post("/api/v1/market/compare", response_model=MarketCompareResponse)
@router.post("/api/market/compare", response_model=MarketCompareResponse)
def compare_markets(request: MarketCompareRequest = Body(...)):
    """
    Compare market prices for a crop across regional mandis with distance indicators
    and transparent decision summaries.
    """
    return compare_market_prices(
        crop=request.crop,
        location=request.location
    )
