from fastapi import APIRouter, Body, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from services.labour_service import get_available_labour, create_labour_booking_request

router = APIRouter(tags=["Labour Booking"])


class WorkerItem(BaseModel):
    id: str
    name: str
    skills: List[str]
    daily_wage: float
    location: str
    availability: str  # available | limited | unavailable
    rating: Optional[float] = None
    data_source: str = "demo"


class LabourAvailableResponse(BaseModel):
    workers: List[WorkerItem]
    disclaimer: str


class LabourBookingRequest(BaseModel):
    worker_id: str
    date: str  # YYYY-MM-DD
    duration_days: int = 1
    task_description: str
    location: str
    contact_phone: Optional[str] = None


class LabourBookingResponse(BaseModel):
    request_id: str
    status: str  # pending | confirmed | rejected
    message: str
    demo_notice: str


@router.get("/api/v1/labour/available", response_model=LabourAvailableResponse)
@router.get("/api/labour/available", response_model=LabourAvailableResponse)
def list_available_labour(skill: Optional[str] = Query(None, description="Optional skill filter")):
    """
    List available farm labour with skills and daily wage rates (Demo data).
    """
    return get_available_labour(skill=skill)


@router.post("/api/v1/labour/request", response_model=LabourBookingResponse)
@router.post("/api/labour/request", response_model=LabourBookingResponse)
def submit_labour_request(request: LabourBookingRequest = Body(...)):
    """
    Submit a demo farm labour booking request.
    """
    return create_labour_booking_request(request.dict())
