"""
AgriDarshak Farmer Chatbot & Voice Assistant Router
Reuses existing AI Advisory service and fallback engine with conversational formatting.
"""
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import html

from database import get_db
from services.gemini_service import generate_interactive_advisory

router = APIRouter(tags=["Chatbot"])


class ChatContext(BaseModel):
    crop: Optional[str] = None
    location: Optional[str] = None
    soil_type: Optional[str] = None
    growth_stage: Optional[str] = None
    weather: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1500, description="Farmer message or query")
    language: Optional[str] = Field("en", description="Target language code: en, or, hi, te, ta, bn, gu, mr")
    context: Optional[ChatContext] = Field(default_factory=ChatContext, description="Optional farmer contextual parameters")


class ChatResponse(BaseModel):
    response: str
    source: str  # "gemini" | "fallback"
    language: str


@router.post("/api/v1/chat", response_model=ChatResponse)
@router.post("/api/chat", response_model=ChatResponse)
def handle_farmer_chat(
    request: ChatRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Process farmer query through AgriDarshak AI Advisory engine with multi-turn context.
    Returns localized AI response or structured fallback.
    """
    raw_message = (request.message or "").strip()
    if not raw_message:
        raise HTTPException(status_code=400, detail="Chat message cannot be empty.")

    # Sanitize user message for security
    clean_message = html.escape(raw_message)

    # Build contextual query for the advisory service
    location = "Vijayawada, Andhra Pradesh"
    crop_name = "Chilli"
    weather_data = None
    soil_type = None

    if request.context:
        if request.context.location:
            location = request.context.location
        if request.context.crop:
            crop_name = request.context.crop
        if request.context.weather:
            weather_data = request.context.weather
        if request.context.soil_type:
            soil_type = request.context.soil_type

    # Format question with soil or growth stage details if provided
    query = clean_message
    if soil_type:
        query = f"[{soil_type} Soil] {query}"

    lang = request.language or "en"
    advisory_text, raw_source = generate_interactive_advisory(
        query=query,
        location=location,
        crop_name=crop_name,
        weather_data=weather_data,
        language=lang,
        return_source=True
    )

    source = "gemini" if raw_source in ["gemini", "ai"] else "fallback"

    return ChatResponse(
        response=advisory_text,
        source=source,
        language=lang
    )
