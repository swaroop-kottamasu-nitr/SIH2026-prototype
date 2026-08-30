from fastapi import APIRouter, Depends, Query, Header, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
from database import get_db
from models.user import User
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


def resolve_authorized_user_id(
    requested_user_id: Optional[int],
    x_user_id: Optional[str] = None,
    authorization: Optional[str] = None,
    db: Session = None
) -> Optional[int]:
    """
    Validate authorization for Farm Health risk queries.
    - If authenticated context is present (X-User-ID or Authorization header), enforce that
      users cannot access another farmer's private farm data.
    - If requested_user_id is supplied without matching authentication, reject unauthorized access.
    - If no user_id is requested, derive it from the authenticated context.
    - If unauthenticated and no user_id is requested, allow generic location assessment.
    """
    authenticated_id: Optional[int] = None

    # Check X-User-ID header
    if x_user_id:
        try:
            authenticated_id = int(x_user_id.strip())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication identifier"
            )
    # Check Authorization: Bearer <id/token>
    elif authorization:
        parts = authorization.strip().split()
        token = parts[1] if len(parts) == 2 else parts[0]
        if token.isdigit():
            authenticated_id = int(token)

    # 1. Authenticated caller attempting to access a different user's private farm data
    if authenticated_id is not None and requested_user_id is not None:
        if authenticated_id != requested_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: You cannot access another farmer's private farm data"
            )

    # 2. Unauthenticated caller attempting to supply an arbitrary private user_id
    if authenticated_id is None and requested_user_id is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Authentication required to access private farm health data"
        )

    # 3. Derive user_id from authenticated session when not explicitly provided
    resolved_id = requested_user_id if requested_user_id is not None else authenticated_id

    # Verify user exists if an ID is resolved
    if resolved_id is not None and db is not None:
        user = db.query(User).filter(User.id == resolved_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farmer profile not found"
            )

    return resolved_id


@router.get("/risk", response_model=FarmRiskResponse)
def get_farm_risk_get(
    user_id: Optional[int] = Query(None, description="Optional user ID for personalized farm health"),
    location: Optional[str] = Query(None, description="Optional location override"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    """
    Get deterministic Farm Health & Distress Risk Assessment (0-100 score).
    Protected: Only authorized farmers can access their own farm health assessment.
    """
    authorized_user_id = resolve_authorized_user_id(
        requested_user_id=user_id,
        x_user_id=x_user_id,
        authorization=authorization,
        db=db
    )
    return calculate_farm_health_risk(db=db, user_id=authorized_user_id, location=location)


@router.post("/risk", response_model=FarmRiskResponse)
def get_farm_risk_post(
    request: FarmRiskRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    """
    POST endpoint for Farm Health & Distress Risk Assessment.
    Protected: Only authorized farmers can access their own farm health assessment.
    """
    authorized_user_id = resolve_authorized_user_id(
        requested_user_id=request.user_id,
        x_user_id=x_user_id,
        authorization=authorization,
        db=db
    )
    return calculate_farm_health_risk(db=db, user_id=authorized_user_id, location=request.location)
