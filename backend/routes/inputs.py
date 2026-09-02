from fastapi import APIRouter, Body
from pydantic import BaseModel, Field
from typing import Optional, List
from services.input_locator_service import search_agricultural_inputs

router = APIRouter(tags=["Input Locator"])


class InputItem(BaseModel):
    name: str
    category: str
    address: Optional[str] = None
    contact: Optional[str] = None
    distance: Optional[float] = None
    data_verified: bool = False


class InputSearchResponse(BaseModel):
    results: List[InputItem]
    data_source: str  # verified | demo | fallback


class InputSearchRequest(BaseModel):
    category: Optional[str] = Field("all", description="seeds | fertilizers | pesticides | equipment | other | all")
    location: Optional[str] = Field("Vijayawada, Andhra Pradesh", description="Optional location")


@router.post("/api/v1/inputs/search", response_model=InputSearchResponse)
@router.post("/api/inputs/search", response_model=InputSearchResponse)
def search_inputs(request: InputSearchRequest = Body(...)):
    """
    Locate certified seeds, bio-fertilizers, pesticides, and farm equipment suppliers.
    """
    return search_agricultural_inputs(
        category=request.category,
        location=request.location
    )
