from fastapi import APIRouter, Body, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from services.schemes_service import get_all_schemes, estimate_scheme_eligibility

router = APIRouter(tags=["Government Schemes"])


class SchemeItem(BaseModel):
    id: str
    name: str
    description: str
    category: str  # subsidy | insurance | loan | training | other
    eligibility: str
    benefits: str
    deadline: Optional[str] = None
    application_link: Optional[str] = None
    data_source: str = "demo"


class SchemesListResponse(BaseModel):
    schemes: List[SchemeItem]
    disclaimer: str


class SchemeEligibilityItem(BaseModel):
    scheme_id: str
    match_reason: str
    confidence: str  # HIGH | MEDIUM | LOW


class SchemeEligibilityResponse(BaseModel):
    eligible_schemes: List[SchemeEligibilityItem]
    disclaimer: str


class SchemeEligibilityRequest(BaseModel):
    crop: Optional[str] = None
    location: Optional[str] = None
    farm_size: Optional[float] = None


@router.get("/api/v1/schemes", response_model=SchemesListResponse)
@router.get("/api/schemes", response_model=SchemesListResponse)
def list_schemes(category: Optional[str] = Query(None, description="subsidy | insurance | loan | training | other")):
    """
    Get directory of central and state agricultural welfare schemes (Demo data).
    """
    return get_all_schemes(category=category)


@router.get("/api/v1/schemes/eligibility", response_model=SchemeEligibilityResponse)
@router.get("/api/schemes/eligibility", response_model=SchemeEligibilityResponse)
def check_eligibility_get(
    crop: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    farm_size: Optional[float] = Query(None)
):
    """
    Check estimated scheme eligibility via GET query.
    """
    return estimate_scheme_eligibility(crop=crop, location=location, farm_size=farm_size)


@router.post("/api/v1/schemes/eligibility", response_model=SchemeEligibilityResponse)
@router.post("/api/schemes/eligibility", response_model=SchemeEligibilityResponse)
def check_eligibility_post(request: SchemeEligibilityRequest = Body(...)):
    """
    Check estimated scheme eligibility via POST payload.
    """
    return estimate_scheme_eligibility(
        crop=request.crop,
        location=request.location,
        farm_size=request.farm_size
    )
