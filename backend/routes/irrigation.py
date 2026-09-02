from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from database import get_db
from models.user import User
from services.irrigation_service import get_irrigation_recommendation

router = APIRouter(tags=["Irrigation"])


class DataAvailableSchema(BaseModel):
    weather_forecast: bool
    rainfall_forecast: bool
    soil_moisture: bool = False
    temperature: bool
    humidity: bool


class IrrigationRecommendationDetail(BaseModel):
    current_crop: str
    next_window: str
    reason: str
    priority: str  # HIGH | MEDIUM | LOW
    expected_benefit: str
    weather_factor: str
    data_available: DataAvailableSchema
    recommendation_type: str  # forecast_based | user_provided | general_guidance


class IrrigationRecommendationResponse(BaseModel):
    recommendation: IrrigationRecommendationDetail


class IrrigationRecommendationRequest(BaseModel):
    crop: str = Field(..., description="Crop name (e.g. Rice, Chilli, Cotton)")
    growth_stage: str = Field("vegetative", description="seedling | vegetative | flowering | fruiting | maturity")
    soil_type: Optional[str] = Field(None, description="Optional soil type (e.g. Clay, Loamy, Black Soil)")
    location: str = Field("Vijayawada, Andhra Pradesh", description="District/block location")
    user_id: Optional[int] = None


@router.post("/api/v1/irrigation/recommendation", response_model=IrrigationRecommendationResponse)
@router.post("/api/irrigation/recommendation", response_model=IrrigationRecommendationResponse)
def get_irrigation_advice(
    request: IrrigationRecommendationRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Generate data-driven irrigation recommendation using live weather forecast,
    crop growth stages, and soil characteristics.
    """
    crop = request.crop
    stage = request.growth_stage
    soil = request.soil_type
    loc = request.location

    # Context enrichment from user profile if user_id is provided
    if request.user_id:
        try:
            user = db.query(User).filter(User.id == request.user_id).first()
            if user:
                if user.location and not request.location:
                    loc = user.location
                if user.preferred_crops and not request.crop:
                    if isinstance(user.preferred_crops, list) and len(user.preferred_crops) > 0:
                        crop = str(user.preferred_crops[0])
                    elif isinstance(user.preferred_crops, str):
                        crop = user.preferred_crops
        except Exception:
            pass

    rec_data = get_irrigation_recommendation(
        crop=crop,
        growth_stage=stage,
        location=loc,
        soil_type=soil
    )
    return rec_data
