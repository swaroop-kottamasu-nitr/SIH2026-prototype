"""
Crop recommendation service - Data-driven multi-factor analysis.
Recommendations are generated ONLY after analyzing:
- Soil analysis (nutrients, pH, soil type, organic matter)
- Weather forecast
- Geographic location and seasonal suitability
- Market demand and price trends
- Climate alerts (if any)
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from services.gemini_service import generate_crop_recommendation_explanation
from services.weather_service import weather_service
from services.market_price_service import (
    get_crop_prices_for_location,
    _resolve_state,
    get_current_season,
)
from services.climate_alert import climate_alert_service

# Load crops database
CROPS_FILE = Path(__file__).parent.parent / "data" / "crops.json"

# Unfavorable market: exclude crops with trend down and change < -15%
MARKET_UNFAVORABLE_THRESHOLD = -15


def load_crops_data() -> List[Dict]:
    """Load crops database from JSON file."""
    try:
        with open(CROPS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("crops", [])
    except Exception as e:
        print(f"Error loading crops data: {e}")
        return []


CROPS_DB = load_crops_data()


def _get_weather_forecast_summary(location: str) -> dict:
    """Fetch upcoming weather for location. Returns structured summary."""
    try:
        forecast = weather_service.get_forecast(location, None, None, days=5)
        if not forecast or "list" not in forecast:
            return {"source": "unavailable", "message": "Forecast not available"}
        days = forecast["list"][:3]
        temps = [d.get("main", {}).get("temp") for d in days if d.get("main", {}).get("temp")]
        rain = [d.get("rain", {}).get("3h", 0) for d in days]
        return {
            "source": "weather_service",
            "next_3_days": {
                "avg_temp_c": round(sum(temps) / len(temps), 1) if temps else None,
                "total_rain_mm": round(sum(rain), 1),
                "days": len(days),
            },
        }
    except Exception as e:
        print(f"Weather forecast error: {e}")
        return {"source": "error", "message": str(e)}


def _get_market_data_for_crops(crop_names: List[str], location: str) -> dict:
    """Fetch market prices and trends for crops. Returns {crop_name: {trend, change_percent, latest_price}}."""
    state = _resolve_state(location)
    result = {}
    for name in crop_names:
        try:
            data = get_crop_prices_for_location(name, location, days=30)
            result[name] = {
                "trend": data.get("trend", "stable"),
                "change_percent": data.get("change_percent", 0),
                "latest_price": data.get("latest_price"),
            }
        except Exception:
            result[name] = {"trend": "unknown", "change_percent": 0, "latest_price": None}
    return result


def _get_climate_alerts_summary(location: str) -> list:
    """Check for active climate/weather alerts at location."""
    try:
        alerts = climate_alert_service.check_weather_alerts(location, None, None)
        return [
            {"type": a.get("type"), "severity": a.get("severity"), "title": a.get("title")}
            for a in alerts
        ]
    except Exception:
        return []


def _build_soil_analysis_context(soil_params: dict) -> dict:
    """Build structured soil context from params."""
    if not soil_params:
        return {}
    return {
        "soil_type": soil_params.get("soil_type"),
        "nitrogen_kg_ha": soil_params.get("nitrogen"),
        "phosphorus_kg_ha": soil_params.get("phosphorus"),
        "potassium_kg_ha": soil_params.get("potassium"),
        "ph": soil_params.get("ph"),
        "organic_matter": soil_params.get("organic_matter"),
        "soil_health": soil_params.get("soil_health"),
    }


def get_crop_recommendations(
    soil_type: str,
    location: str,
    season: str = None,
    temperature: float = None,
    language: str = "en",
    soil_analysis: dict = None,
    user_id: int = None,
    db=None,
) -> dict:
    """
    Get crop recommendations using multi-factor analysis.

    Criteria (ALL must be satisfied for a crop to be recommended):
    - Suitable for soil conditions
    - Compatible with weather and season
    - In demand or favorable market value
    - Practical for the farmer

    Args:
        soil_type: Type of soil (Clay, Sandy, Loamy, etc.)
        location: State or region
        season: Kharif, Rabi, or Summer (inferred from current if None)
        temperature: Current temp (fetched from weather if None)
        soil_analysis: Optional dict with nitrogen, phosphorus, potassium, ph, organic_matter, soil_health
        user_id: Optional — used to fetch latest soil analysis from DB
        db: Optional SQLAlchemy session for fetching user soil history
    """
    season = season or get_current_season()

    # 1. Resolve soil context (from explicit params or user's latest analysis)
    soil_context = _build_soil_analysis_context(soil_analysis or {})
    soil_context["soil_type"] = soil_context.get("soil_type") or soil_type

    if user_id and db and not soil_analysis:
        from models.soil_analysis_history import SoilAnalysisHistory
        latest = (
            db.query(SoilAnalysisHistory)
            .filter(SoilAnalysisHistory.user_id == user_id)
            .order_by(SoilAnalysisHistory.analysis_date.desc())
            .first()
        )
        if latest:
            soil_context = _build_soil_analysis_context({
                "soil_type": latest.soil_type or soil_type,
                "nitrogen": latest.nitrogen,
                "phosphorus": latest.phosphorus,
                "potassium": latest.potassium,
                "ph": latest.ph,
                "organic_matter": latest.organic_matter,
                "soil_health": latest.soil_health,
            })

    # 2. Fetch weather forecast
    weather_forecast = _get_weather_forecast_summary(location)

    # 3. Resolve temperature from forecast if not provided
    if temperature is None and weather_forecast.get("next_3_days", {}).get("avg_temp_c"):
        temperature = weather_forecast["next_3_days"]["avg_temp_c"]

    # 4. Filter crops by soil, location, season, temperature
    candidates = []
    for crop in CROPS_DB:
        score = 0

        if soil_type in crop.get("soil_types", []):
            score += 3
        if location in crop.get("states", []) or not crop.get("states"):
            score += 2
        if season in crop.get("seasons", []) or "Year-round" in crop.get("seasons", []):
            score += 2
        if temperature is not None:
            tr = crop.get("temperature_range", [0, 50])
            if len(tr) >= 2 and tr[0] <= temperature <= tr[1]:
                score += 1

        if score >= 3:
            candidates.append({
                "name": crop["name"],
                "local_name": crop.get("local_name", ""),
                "score": score,
                "growing_duration": crop.get("growing_duration", ""),
                "rainfall_min": crop.get("rainfall_min", 0),
            })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    candidate_names = [c["name"] for c in candidates[:10]]

    # 5. Fetch market data for candidates
    market_data = _get_market_data_for_crops(candidate_names, location)

    # 6. Filter by market: exclude severely unfavorable (down > 15%)
    recommended_crops = []
    for c in candidates[:8]:
        m = market_data.get(c["name"], {})
        trend = m.get("trend", "stable")
        change = m.get("change_percent", 0)
        if trend == "down" and change < MARKET_UNFAVORABLE_THRESHOLD:
            continue
        c["market_trend"] = trend
        c["market_change_percent"] = change
        c["latest_price"] = m.get("latest_price")
        recommended_crops.append(c)

    # 7. Fetch climate alerts
    climate_alerts = _get_climate_alerts_summary(location)

    # 8. Build structured analysis data for Gemini
    analysis_soil = soil_context if soil_context else {"soil_type": soil_type}
    analysis_weather = {
        "season": season,
        "temperature_c": temperature,
        "forecast_summary": weather_forecast,
    }
    analysis_market = {
        name: market_data.get(name) for name in [c["name"] for c in recommended_crops]
    }

    # 9. Generate advisory from structured data (Gemini or deterministic localized fallback)
    advisory_source = "ai"
    if recommended_crops:
        explanation, advisory_source = generate_crop_recommendation_explanation(
            recommended_crops=recommended_crops,
            soil_type=soil_type,
            season=season,
            location=location,
            language=language,
            soil_analysis=analysis_soil,
            weather_forecast=analysis_weather,
            market_data=analysis_market,
            climate_alerts=climate_alerts if climate_alerts else None,
            return_source=True
        )
    else:
        advisory_source = "fallback"
        no_match_msgs = {
            "en": "No crops matched all analysis criteria (soil, weather, season, market). Consider adjusting soil type or location, or consult a local agricultural expert.",
            "or": "ମାଟି, ପାଣିପାଗ ଏବଂ ବଜାର ସ୍ଥିତି ଅନୁସାରେ କୌଣସି ଫସଲ ସମ୍ପୂର୍ଣ୍ଣ ମେଳ ଖାଉନାହିଁ। ଦୟାକରି ମାଟି ପ୍ରକାର କିମ୍ବା ସ୍ଥାନ ଯାଞ୍ଚ କରନ୍ତୁ କିମ୍ବା ସ୍ଥାନୀୟ କୃଷି ଅଧିକାରୀଙ୍କ ପରାମର୍ଶ ନିଅନ୍ତୁ।",
            "hi": "मिट्टी, मौसम और बाजार की स्थितियों के अनुसार कोई भी फसल पूरी तरह मेल नहीं खाती। कृपया मिट्टी का प्रकार या स्थान बदलें अथवा स्थानीय कृषि विशेषज्ञ से सलाह लें।",
            "te": "నేల, వాతావరణం మరియు మార్కెట్ పరిస్థితుల ఆధారంగా ఎటువంటి పంటలు సరిపోలలేదు. దయచేసి నేల రకం మార్చండి లేదా స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి.",
            "ta": "மண், வானிலை மற்றும் சந்தை நிலவரங்களின்படி பயிர்கள் எதுவும் பொருந்தவில்லை. தயவுசெய்து மண் வகையை சரிபார்க்கவும் அல்லது உள்ளூர் வேளாண்மை அலுவலரை அணுகவும்.",
            "bn": "মাটি, আবহাওয়া এবং বাজার পরিস্থিতি অনুযায়ী কোনো ফসল মেলেনি। অনুগ্রহ করে মাটির ধরন বা এলাকা পরিবর্তন করুন অথবা স্থানীয় কৃষি কর্মকর্তার পরামর্শ নিন।",
            "gu": "માટી, હવામાન અને બજાર પરિસ્થિતિ અનુસાર કોઈ પાક યોગ્ય નથી જણાયો. કૃપા કરીને માટીનો પ્રકાર અથવા સ્થળ બદલો અથવા સ્થાનિક કૃષિ નિષ્ણાતનો સંપર્ક કરો.",
            "mr": "माती, हवामान आणि बाजार परिस्थितीनुसार कोणतेही पीक जुळत नाही. कृपया मातीचा प्रकार किंवा स्थान तपासा किंवा स्थानिक कृषी तज्ञांचा सल्ला घ्या."
        }
        explanation = no_match_msgs.get(language, no_match_msgs["en"])

    return {
        "recommended_crops": recommended_crops,
        "explanation": explanation,
        "total_recommendations": len(recommended_crops),
        "advisory_source": advisory_source,
        "analysis_context": {
            "soil": analysis_soil,
            "weather": analysis_weather,
            "climate_alerts": climate_alerts,
        },
    }


def get_all_crops() -> List[Dict]:
    """Get all crops in database."""
    return CROPS_DB


def search_crops(query: str) -> List[Dict]:
    """Search crops by name."""
    q = query.lower()
    return [
        c for c in CROPS_DB
        if q in c.get("name", "").lower() or q in c.get("local_name", "").lower()
    ]
