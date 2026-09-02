from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from database import get_db
from models.user import User
from services.gemini_service import generate_interactive_advisory

router = APIRouter(tags=["Advisory"])


class AdvisoryStructuredGuidance(BaseModel):
    situation: str
    recommended_actions: List[str]
    reasoning: str
    priority: str  # HIGH | MEDIUM | LOW
    expected_benefit: str


class AdvisoryRequest(BaseModel):
    question: Optional[str] = Field(None, description="The farmer's question or advisory prompt")
    query: Optional[str] = Field(None, description="Alias for question")
    language: Optional[str] = Field("en", description="Language code: en, or, hi, te, ta, bn, gu, mr")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contextual farm data: crop, location, weather, soil, distress_score")
    
    # Flat optional fields for backward compatibility
    location: Optional[str] = None
    crop_name: Optional[str] = None
    season: Optional[str] = None
    temperature: Optional[float] = None
    weather_data: Optional[Dict[str, Any]] = None
    distress_score: Optional[int] = None
    user_id: Optional[int] = None


class AdvisoryResponse(BaseModel):
    advisory: str
    source: str  # "gemini" | "fallback"
    advisory_source: str  # "ai" | "fallback"
    language: str
    question: Optional[str] = None
    structured_guidance: Optional[Dict[str, Any]] = None


def _extract_request_context(request: AdvisoryRequest, db: Session):
    """Extract and normalize question and contextual parameters from request."""
    # Resolve question / query
    question_text = (request.question or request.query or "").strip()
    if not question_text:
        question_text = "General field management and distress prevention advice"

    lang = request.language or "en"
    ctx = request.context or {}

    # Context extraction with cascade: ctx -> flat param -> user db -> default
    crop = ctx.get("crop") or ctx.get("crop_name") or request.crop_name or "Chilli"
    location = ctx.get("location") or request.location or "Vijayawada, Andhra Pradesh"
    season = ctx.get("season") or request.season or "Kharif"
    temperature = ctx.get("temperature") or ctx.get("temp") or request.temperature or 28.0
    weather = ctx.get("weather") or ctx.get("weather_data") or request.weather_data
    distress_score = ctx.get("distress_score") or request.distress_score

    user_id = request.user_id or ctx.get("user_id")
    if user_id:
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                if (not request.language or request.language == "en") and user.language:
                    lang = user.language
                if user.location and not (ctx.get("location") or request.location):
                    location = user.location
                if user.preferred_crops and not (ctx.get("crop") or request.crop_name):
                    if isinstance(user.preferred_crops, list) and len(user.preferred_crops) > 0:
                        crop = str(user.preferred_crops[0])
                    elif isinstance(user.preferred_crops, str):
                        crop = user.preferred_crops
        except Exception:
            pass

    return {
        "question": question_text,
        "language": lang,
        "crop": crop,
        "location": location,
        "season": season,
        "temperature": float(temperature) if temperature else 28.0,
        "weather_data": weather,
        "distress_score": int(distress_score) if distress_score is not None else None,
        "user_id": user_id
    }


def _parse_structured_guidance(advisory_text: str, fallback_priority: str = "HIGH") -> Dict[str, Any]:
    """Parse advisory markdown into structured dictionary format."""
    lines = advisory_text.splitlines()
    situation_lines = []
    actions = []
    reasoning_lines = []
    priority = fallback_priority
    benefit_lines = []

    current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("## "):
            header = stripped[3:].lower()
            if any(k in header for k in ["situation", "context", "ସ୍ଥିତି", "स्थिति", "పరిస్థితి", "நிலை", "পরিস্থিতি", "સ્થિતિ", "सद्यस्थिती", "summary", "ସାରାଂଶ", "सारांश"]):
                current_section = "situation"
            elif any(k in header for k in ["action", "recommend", "ପଦକ୍ଷେପ", "कदम", "చర్యలు", "நடவடிக்கைகள்", "পদক্ষেপ", "પગલાં", "कृती", "treatment"]):
                current_section = "actions"
            elif any(k in header for k in ["why", "matter", "reason", "କାରଣ", "क्यों", "ప్రాముఖ్యత", "முக்கியத்துவம்", "গুরুত্বপূর্ণ", "શા માટે", "महत्त्व"]):
                current_section = "reasoning"
            elif any(k in header for k in ["priority", "ପ୍ରାଥମିକତା", "प्राथमिकता", "ప్రాధాన్యత", "முன்னுரிமை", "অগ্রাধিকার", "પ્રાથમિકતા", "प्राधान्यता"]):
                current_section = "priority"
            elif any(k in header for k in ["benefit", "expect", "ଲାଭ", "लाभ", "ప్రయోజనం", "நன்மை", "সুফল", "લાભ", "फायदा"]):
                current_section = "benefit"
            else:
                current_section = "situation"
            continue

        if current_section == "situation":
            situation_lines.append(stripped)
        elif current_section == "actions":
            clean_action = stripped
            if clean_action.startswith(("-", "*", "•")) or (len(clean_action) > 2 and clean_action[0].isdigit() and clean_action[1] in ". "):
                clean_action = clean_action.lstrip("-*•0123456789. ")
            if clean_action:
                actions.append(clean_action)
        elif current_section == "reasoning":
            reasoning_lines.append(stripped)
        elif current_section == "priority":
            upper = stripped.upper()
            if "URGENT" in upper or "HIGH" in upper:
                priority = "HIGH"
            elif "TODAY" in upper or "MEDIUM" in upper:
                priority = "HIGH"
            elif "THIS WEEK" in upper or "LOW" in upper:
                priority = "MEDIUM"
        elif current_section == "benefit":
            benefit_lines.append(stripped)

    # Fallback defaults if parsing is sparse
    if not actions:
        actions = [
            "Inspect underside of leaves and apical shoots for pest activity or early fungal lesions.",
            "Maintain clean field drainage furrows to prevent root-zone water stagnation.",
            "Apply recommended bio-pesticide (Neem oil @ 5ml/L) or balanced nutrient top-dressing."
        ]

    return {
        "situation": " ".join(situation_lines) if situation_lines else "Field conditions evaluated for optimal crop protection.",
        "recommended_actions": actions[:5],
        "reasoning": " ".join(reasoning_lines) if reasoning_lines else "Timely intervention mitigates abiotic and biotic stresses before economic damage thresholds are reached.",
        "priority": priority,
        "expected_benefit": " ".join(benefit_lines) if benefit_lines else "Prevents 20-35% potential yield loss and safeguards crop health."
    }


@router.post("/api/v1/advisory", response_model=AdvisoryResponse)
@router.post("/advisory", response_model=AdvisoryResponse)
def get_v1_advisory(
    request: AdvisoryRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Primary API v1 Advisory Endpoint.
    Generates structured, contextual farm advisory via Gemini AI with deterministic rule-based fallback.
    """
    ctx = _extract_request_context(request, db)

    advisory_text, raw_source = generate_interactive_advisory(
        query=ctx["question"],
        location=ctx["location"],
        crop_name=ctx["crop"],
        season=ctx["season"],
        temperature=ctx["temperature"],
        weather_data=ctx["weather_data"],
        distress_score=ctx["distress_score"],
        user_id=ctx["user_id"],
        language=ctx["language"],
        return_source=True
    )

    # Normalize source name: "gemini" or "fallback"
    source = "gemini" if raw_source in ["gemini", "ai"] else "fallback"
    advisory_source = "ai" if source == "gemini" else "fallback"

    structured = _parse_structured_guidance(advisory_text)

    return AdvisoryResponse(
        advisory=advisory_text,
        source=source,
        advisory_source=advisory_source,
        language=ctx["language"],
        question=ctx["question"],
        structured_guidance=structured
    )
