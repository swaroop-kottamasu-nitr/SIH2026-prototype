from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from database import get_db
from models.user import User
from models.crop_history import CropHistory
from services.crop_rotation_service import get_crop_rotation_recommendations

router = APIRouter(tags=["Crop Rotation"])


class CropRotationItem(BaseModel):
    crop: str
    reason: str
    soil_benefit: str
    pest_break_benefit: Optional[str] = None
    season_suitability: str  # HIGH | MEDIUM | LOW
    confidence: str  # HIGH | MEDIUM | LOW


class CropRotationResponse(BaseModel):
    recommendations: List[CropRotationItem]
    data_source: str  # history_based | generalized


class CropRotationRequest(BaseModel):
    previous_crop: str = Field(..., description="Previous season standing crop")
    current_crop: Optional[str] = Field(None, description="Optional current crop")
    season: str = Field("rabi", description="Target upcoming season: kharif | rabi | zaid/summer")
    soil_type: Optional[str] = Field(None, description="Optional soil type")
    crop_history: Optional[List[str]] = Field(default_factory=list, description="List of previous crops grown in the field")
    user_id: Optional[int] = None


@router.post("/api/v1/crop-rotation/recommendation", response_model=CropRotationResponse)
@router.post("/api/crop-rotation/recommendation", response_model=CropRotationResponse)
def get_crop_rotation_advice(
    request: CropRotationRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Generate agronomic crop rotation recommendations to break pest cycles,
    restore nitrogen and organic carbon, and prevent soil exhaustion.
    """
    prev_crop = request.previous_crop
    season = request.season
    soil = request.soil_type
    history = list(request.crop_history or [])

    # If user_id provided and no history passed in body, fetch user's CropHistory from database
    if request.user_id and not history:
        try:
            db_history = db.query(CropHistory).filter(CropHistory.user_id == request.user_id).order_by(CropHistory.planting_date.desc()).limit(5).all()
            if db_history:
                history = [h.crop_name for h in db_history if h.crop_name]
                if not prev_crop and len(history) > 0:
                    prev_crop = history[0]
        except Exception:
            pass

    rot_data = get_crop_rotation_recommendations(
        previous_crop=prev_crop,
        season=season,
        current_crop=request.current_crop,
        soil_type=soil,
        crop_history=history
    )
    return rot_data
