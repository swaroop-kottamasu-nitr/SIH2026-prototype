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
    language: Optional[str] = "en"


from typing import Optional, List, Dict, Any


class RiskFactorResponse(BaseModel):
    name: str
    score: int
    max_score: int
    level: str
    reason: str
    key: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


class FarmRiskResponse(BaseModel):
    score: int
    risk_level: str
    factors: List[RiskFactorResponse]
    recommendations: List[str]
    recommendation_objects: Optional[List[Any]] = None


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
                detail="Invalid user identification header format"
            )

    # Check Bearer JWT token header
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            from services.auth import verify_token
            payload = verify_token(token)
            if payload and "sub" in payload:
                user_email = payload["sub"]
                if db:
                    u = db.query(User).filter(User.email == user_email).first()
                    if u:
                        authenticated_id = u.id
        except Exception:
            pass

    # Authorization enforcement:
    # 1. If user is authenticated, ensure they cannot query another user's private data
    if authenticated_id is not None and requested_user_id is not None:
        if authenticated_id != requested_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot access farm health assessment of another farmer"
            )

    # 2. If client requests a specific user_id but provides no auth headers at all, block access
    if requested_user_id is not None and authenticated_id is None:
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
    language: Optional[str] = Query("en", description="Selected UI language"),
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
    return calculate_farm_health_risk(db=db, user_id=authorized_user_id, location=location, language=language)


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
    return calculate_farm_health_risk(db=db, user_id=authorized_user_id, location=request.location, language=request.language)


class InteractiveAdvisoryRequest(BaseModel):
    query: Optional[str] = ""
    location: Optional[str] = "Vijayawada, Andhra Pradesh"
    crop_name: Optional[str] = "Chilli"
    season: Optional[str] = "Kharif"
    temperature: Optional[float] = 28.0
    weather_data: Optional[dict] = None
    distress_score: Optional[int] = None
    user_id: Optional[int] = None
    language: Optional[str] = "en"


class InteractiveAdvisoryResponse(BaseModel):
    advisory: str
    explanation: Optional[str] = None
    advisory_source: str = "ai"
    query: Optional[str] = None
    language: str = "en"


@router.post("/advisory", response_model=InteractiveAdvisoryResponse)
def get_interactive_advisory(
    request: InteractiveAdvisoryRequest,
    db: Session = Depends(get_db)
):
    """
    Generate customized AI farm advisory or rule-based fallback advisory.
    Responds to farmer queries with immediate deterministic fallback.
    """
    from services.gemini_service import generate_interactive_advisory

    lang = request.language
    crop = request.crop_name or "Chilli"
    location = request.location or "Vijayawada, Andhra Pradesh"

    if request.user_id:
        user = db.query(User).filter(User.id == request.user_id).first()
        if user:
            if not lang and user.language:
                lang = user.language
            if user.preferred_crops and not request.crop_name:
                if isinstance(user.preferred_crops, list) and len(user.preferred_crops) > 0:
                    crop = str(user.preferred_crops[0])
                elif isinstance(user.preferred_crops, str):
                    crop = user.preferred_crops
            if user.location and not request.location:
                location = user.location

    lang = lang or "en"
    query_text = request.query or "General field management and distress prevention advice"

    advisory_text, source = generate_interactive_advisory(
        query=query_text,
        location=location,
        crop_name=crop,
        season=request.season or "Kharif",
        temperature=request.temperature or 28.0,
        weather_data=request.weather_data,
        distress_score=request.distress_score,
        user_id=request.user_id,
        language=lang,
        return_source=True
    )

    return InteractiveAdvisoryResponse(
        advisory=advisory_text,
        explanation=advisory_text,
        advisory_source=source,
        query=request.query,
        language=lang
    )

