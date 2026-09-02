from fastapi import APIRouter, Body
from pydantic import BaseModel, Field
from typing import Optional, List
from services.storage_locator_service import search_storage_facilities

router = APIRouter(tags=["Storage Locator"])


class StorageFacilityItem(BaseModel):
    name: str
    type: str  # Warehouse | Cold Storage | Godown | Silo
    location: str
    capacity: Optional[str] = None
    contact: Optional[str] = None
    distance: Optional[float] = None
    capacity_known: bool = False
    availability_confirmed: bool = False


class StorageSearchResponse(BaseModel):
    facilities: List[StorageFacilityItem]
    data_source: str  # verified | demo | fallback


class StorageSearchRequest(BaseModel):
    crop: Optional[str] = Field(None, description="Crop name")
    quantity: Optional[float] = Field(None, description="Quantity in quintals")
    location: Optional[str] = Field("Vijayawada, Andhra Pradesh", description="Farmer location")


@router.post("/api/v1/storage/search", response_model=StorageSearchResponse)
@router.post("/api/storage/search", response_model=StorageSearchResponse)
def search_storage(request: StorageSearchRequest = Body(...)):
    """
    Locate nearby state warehousing godowns, cold chain facilities, and grain silos.
    """
    return search_storage_facilities(
        crop=request.crop,
        quantity=request.quantity,
        location=request.location
    )
