from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
from database import get_db
from services.farm_health_service import calculate_farm_health_risk

router = APIRouter(prefix="/api/farm-health", tags=["Farm Health & Distress Risk"])


class FarmRiskRequest(BaseModel):
    user_id: Optional[int] = None
    location: Optional[str] = None


class RiskFactorResponse(BaseModel):
    name: str
    score: int
    max_score: int
    level: str
    reason: str


class FarmRiskResponse(BaseModel):
    score: int
    risk_level: str
    factors: List[RiskFactorResponse]
    recommendations: List[str]


@router.get("/risk", response_model=FarmRiskResponse)
def get_farm_risk_get(
    user_id: Optional[int] = Query(None, description="Optional user ID for personalized farm health"),
    location: Optional[str] = Query(None, description="Optional location override"),
    db: Session = Depends(get_db)
):
    """
    Get deterministic Farm Health & Distress Risk Assessment (0-100 score).
    Evaluates Weather, Disease, Market, Crop/Yield, Soil, and Context risks.
    """
    return calculate_farm_health_risk(db=db, user_id=user_id, location=location)


@router.post("/risk", response_model=FarmRiskResponse)
def get_farm_risk_post(
    request: FarmRiskRequest,
    db: Session = Depends(get_db)
):
    """
    POST endpoint for Farm Health & Distress Risk Assessment.
    """
    return calculate_farm_health_risk(db=db, user_id=request.user_id, location=request.location)
