"""
Gemini API service - Uses google-genai SDK (matches reference implementation).
Optimized for FREE tier with strict quota protection.
"""
from config import get_settings
import time
import hashlib
import threading
from typing import Dict, Optional

settings = get_settings()

# Initialize client with API key (same pattern as reference)
_api_key = settings.gemini_api_key or ""
_client = None
_client_lock = threading.Lock()


def _get_client():
    """Get or create Gemini client; uses GEMINI_API_KEY from env if not in settings."""
    global _client
    with _client_lock:
        if _client is not None:
            return _client
        api_key = _api_key or ""
        if not api_key:
            import os
            api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            print("[GEMINI] ERROR: No API key. Set GEMINI_API_KEY in .env")
            return None
        try:
            from google import genai
            from google.genai import types

            _client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=12000)
            )
            print("[GEMINI] Client initialized successfully")
            return _client
        except ImportError:
            print("[GEMINI] google-genai SDK not installed")
            return None
        except Exception as e:
            print(f"[GEMINI] Failed to create client: {e}")
            return None


# ===== FREE TIER PROTECTION =====

_api_lock = threading.Lock()
_response_cache: Dict[str, tuple] = {}
CACHE_DURATION_SEC = 60
_last_request_time = 0
MIN_REQUEST_INTERVAL = 1.0


def _get_cache_key(prompt: str, temperature: float) -> str:
    return hashlib.md5(f"{prompt}_{temperature}".encode()).hexdigest()


def _get_cached(cache_key: str) -> Optional[str]:
    now = time.time()
    if cache_key in _response_cache:
        text, stored_at = _response_cache[cache_key]
        if now - stored_at < CACHE_DURATION_SEC:
            print("[CACHE] Hit - saved API quota")
            return text
        del _response_cache[cache_key]
    return None


def _save_to_cache(cache_key: str, text: str):
    _response_cache[cache_key] = (text, time.time())
    now = time.time()
    to_remove = [k for k, (_, t) in _response_cache.items() if now - t >= CACHE_DURATION_SEC]
    for k in to_remove:
        del _response_cache[k]


def _wait_rate_limit():
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        wait = MIN_REQUEST_INTERVAL - elapsed
        time.sleep(min(wait, 1.0))
    _last_request_time = time.time()


def get_gemini_response(prompt: str, temperature: float = 0.7, use_cache: bool = True, return_source: bool = False):
    """
    Get Gemini response using google-genai SDK.
    Tries active production models with timeout and automatic graceful fallback.
    Returns text (or tuple of (text, source) if return_source=True).
    """
    cache_key = _get_cache_key(prompt, temperature)

    if use_cache:
        cached = _get_cached(cache_key)
        if cached:
            return (cached, "gemini") if return_source else cached

    acquired = _api_lock.acquire(timeout=2.0)
    if not acquired:
        print("[GEMINI] Concurrency threshold reached. Returning deterministic fallback.")
        return ("", "fallback") if return_source else ""

    try:
        if use_cache:
            cached = _get_cached(cache_key)
            if cached:
                return (cached, "gemini") if return_source else cached

        _wait_rate_limit()

        client = _get_client()
        if not client:
            return ("", "fallback") if return_source else ""

        from google.genai import types

        # Production model candidates in order of preference
        models_to_try = [
            "gemini-3.5-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash-lite"
        ]
        
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=temperature),
                )
                result = response.text.strip() if response.text else ""
                if result:
                    if use_cache:
                        _save_to_cache(cache_key, result)
                    return (result, "gemini") if return_source else result
            except Exception as e:
                err_name = type(e).__name__
                err_msg = str(e)
                # If API quota is exhausted, immediately hand off to deterministic fallback
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    print(f"[GEMINI] Daily API key quota limit reached. Immediate handoff to deterministic fallback engine.")
                    return ("", "fallback") if return_source else ""
                elif "401" in err_msg or "API_KEY_INVALID" in err_msg:
                    print(f"[GEMINI] Authentication error: Invalid API key. Immediate fallback handoff.")
                    return ("", "fallback") if return_source else ""
                elif "404" in err_msg or "NOT_FOUND" in err_msg:
                    continue
                else:
                    print(f"[GEMINI] Model '{model_name}' error: {err_name}. Trying next candidate.")
                    continue

        print("[GEMINI] Upstream AI models unavailable. Activating deterministic agronomic fallback engine.")
        return ("", "fallback") if return_source else ""
    finally:
        _api_lock.release()


# Shared format instructions for all advisories (UI-ready, structured)
_FORMAT_RULES = """
OUTPUT FORMAT (STRICT):
- Use markdown headings (##) and bullet points.
- Start with a 2–3 line Summary. No greetings (no "Namaste", "Dear farmer", etc.).
- Keep sentences short. No long paragraphs or storytelling.
- Be direct, practical, and farmer-friendly.
"""

# CRITICAL: Prevents blind/generic recommendations. Must stay in all prompts.
_CONTROL_SENTENCE = (
    "Do not generate generic recommendations. Base suggestions strictly on the provided "
    "analysis parameters and explain reasoning explicitly."
)


LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "bn": "Bengali",
    "gu": "Gujarati",
    "mr": "Marathi",
    "or": "Odia",
    "od": "Odia",
}

# Native script examples for stronger translation enforcement
LANG_SCRIPTS = {
    "hi": "हिन्दी",
    "te": "తెలుగు",
    "ta": "தமிழ்",
    "bn": "বাংলা",
    "gu": "ગુજરાતી",
    "mr": "मराठी",
    "or": "ଓଡ଼ିଆ",
    "od": "ଓଡ଼ିଆ",
}


def _lang_instruction(language: str) -> str:
    """Returns strong, explicit language instruction for Gemini to output in the requested language."""
    if not language or language == "en":
        return ""
    lang_name = LANG_NAMES.get(language, language)
    script = LANG_SCRIPTS.get(language, "")
    script_part = f" ({script})" if script else ""
    return (
        f"\n\nCRITICAL LANGUAGE RULE: Generate the ENTIRE response ONLY in {lang_name}{script_part}. "
        f"Every heading, bullet point, and sentence must be in {lang_name}. Do NOT use English or any other language. "
        f"Use {lang_name} script and vocabulary appropriate for Indian farmers."
    )


from services.advisory_fallback import (
    build_disease_fallback,
    build_soil_fallback,
    build_crop_fallback,
    build_soil_type_fallback,
    build_market_fallback,
    build_interactive_advisory_fallback
)


def generate_disease_advisory(
    disease_name: str,
    confidence: float,
    crop_name: str = "crop",
    crop_type: str = None,
    language: str = "en",
    return_source: bool = False,
):
    """Generate disease advisory: explanation, severity, treatment. UI-ready format."""
    lang_instruction = _lang_instruction(language)
    crop = crop_name or crop_type or "crop"
    prompt = f"""Generate a structured advisory for DISEASE DETECTION module.
{_FORMAT_RULES}

ANALYSIS DATA (use ONLY this — do not invent):
- Crop: {crop}
- Identified condition: {disease_name}
- Confidence: {confidence:.1%}

{_CONTROL_SENTENCE}

OUTPUT STRUCTURE (use these exact headings):
## Summary
(2–3 lines: what was detected, severity level, key implication)

## Analysis
- What this condition means for {crop}
- How it affects the plant
- Typical severity and spread

## Treatment
- Immediate actions (bullet list)
- Recommended products/methods if applicable

## Prevention
- Steps to avoid recurrence
- Best practices

## Key Actions
- List 3–5 short, actionable items
- When to consult an expert{lang_instruction}"""
    use_cache = (language or "en") == "en"
    ai_text, source = get_gemini_response(prompt, temperature=0.6, use_cache=use_cache, return_source=True)
    if not ai_text:
        fallback_text = build_disease_fallback(disease_name=disease_name, confidence=confidence, crop_name=crop, language=language)
        return (fallback_text, "fallback") if return_source else fallback_text
    return (ai_text, "ai") if return_source else ai_text


def generate_climate_advisory(event_type: str, severity: str, location: str, weather_data: dict, language: str = "en") -> str:
    """Generate climate advisory: risk, timeline, preventive measures. UI-ready format."""
    lang_instruction = _lang_instruction(language)
    prompt = f"""Generate a structured advisory for CLIMATE ALERTS module.
{_FORMAT_RULES}

ANALYSIS DATA (use ONLY this — do not invent):
- Location: {location}
- Event: {event_type}
- Severity: {severity}
- Weather: {weather_data}

{_CONTROL_SENTENCE}

OUTPUT STRUCTURE (use these exact headings):
## Summary
(2–3 lines: what is happening, when, and main risk)

## Risk Explanation
- What this event means for crops
- Which crops are most at risk
- Expected timeline

## Preventive Measures
- Immediate protective actions (bullet list)
- Short-term precautions

## Key Actions
- List 3–5 short, actionable items{lang_instruction}"""
    use_cache = (language or "en") == "en"
    return get_gemini_response(prompt, temperature=0.5, use_cache=use_cache)


def generate_crop_recommendation_explanation(
    recommended_crops: list,
    soil_type: str,
    season: str,
    location: str,
    language: str = "en",
    soil_analysis: dict = None,
    weather_forecast: dict = None,
    market_data: dict = None,
    climate_alerts: list = None,
    return_source: bool = False,
):
    """
    Generate crop recommendation advisory from STRUCTURED ANALYSIS DATA.
    Workflow: Data Analysis → Structured Parameters → Gemini → Formatted Advisory.
    Falls back to deterministic localized advisory if Gemini is unavailable.
    """
    lang_instruction = _lang_instruction(language)
    crops_list = ", ".join(c.get("name", c) if isinstance(c, dict) else c for c in recommended_crops)

    data_parts = [
        f"Location: {location}",
        f"Soil Type: {soil_type}",
        f"Season: {season}",
        f"Recommended Crops (pre-filtered by analysis): {crops_list}",
    ]
    if soil_analysis:
        data_parts.append(f"Soil Analysis: {soil_analysis}")
    if weather_forecast:
        data_parts.append(f"Weather Forecast: {weather_forecast}")
    if market_data:
        data_parts.append(f"Market Data (prices, trends): {market_data}")
    if climate_alerts:
        data_parts.append(f"Active Climate Alerts: {climate_alerts}")

    data_block = "\n".join(f"- {p}" for p in data_parts)

    prompt = f"""Generate a structured advisory for CROP RECOMMENDATION module.
{_FORMAT_RULES}

ANALYSIS DATA (use ONLY this — do not invent or assume):
{data_block}

{_CONTROL_SENTENCE}

For each recommended crop, explain: why suitable for soil and climate; expected benefits and economic advantage; basic cultivation guidance; precautions if risks exist (e.g. from climate alerts or market).

OUTPUT STRUCTURE (use these exact headings):
## Summary
(2–3 lines: why these crops suit the analyzed conditions; reference concrete data)

## Suitability
- Why each crop fits soil and season (cite parameters)
- Compatibility with {location}

## Benefits
- Expected benefits per crop
- Market/demand context if provided
- Growing duration (brief)

## Care Steps
- Basic requirements for success
- Key cultivation tips

## Key Actions
- List 3–5 short, actionable items{lang_instruction}"""
    use_cache = (language or "en") == "en"
    ai_text, source = get_gemini_response(prompt, use_cache=use_cache, return_source=True)
    if not ai_text:
        fallback_text = build_crop_fallback(
            recommended_crops=recommended_crops,
            soil_type=soil_type,
            season=season,
            location=location,
            language=language
        )
        return (fallback_text, "fallback") if return_source else fallback_text
    return (ai_text, "ai") if return_source else ai_text


def generate_soil_analysis_explanation(soil_params: dict, fertilizer_recommendations: list, language: str = "en", return_source: bool = False):
    """Generate soil analysis advisory: nutrients, condition, fertilizer guidance. UI-ready format."""
    lang_instruction = _lang_instruction(language)
    fertilizer_str = ", ".join(fertilizer_recommendations)
    prompt = f"""Generate a structured advisory for SOIL ANALYSIS module.
{_FORMAT_RULES}

ANALYSIS DATA (use ONLY this — do not invent):
- Soil Parameters: {soil_params}
- Recommended Fertilizers: {fertilizer_str}

{_CONTROL_SENTENCE}

OUTPUT STRUCTURE (use these exact headings):
## Summary
(2–3 lines: soil condition overview, main finding)

## Nutrient Analysis
- What each parameter indicates
- Strengths and deficiencies

## Fertilizer Guidance
- Why each recommended fertilizer
- Application doses and timing

## Precautions
- Application guidelines
- Safety and mixing notes

## Key Actions
- List 3–5 short, actionable items{lang_instruction}"""
    use_cache = (language or "en") == "en"
    ai_text, source = get_gemini_response(prompt, use_cache=use_cache, return_source=True)
    if not ai_text:
        fallback_text = build_soil_fallback(soil_params=soil_params, fertilizer_recommendations=fertilizer_recommendations, language=language)
        return (fallback_text, "fallback") if return_source else fallback_text
    return (ai_text, "ai") if return_source else ai_text


def generate_soil_type_explanation(soil_type: str, characteristics: dict, language: str = "en", return_source: bool = False):
    """Generate soil type advisory: nutrients, condition, suitability. UI-ready format."""
    lang_instruction = _lang_instruction(language)
    prompt = f"""Generate a structured advisory for SOIL TYPE (manual selection) module.
{_FORMAT_RULES}

ANALYSIS DATA (use ONLY this — do not invent):
- Soil Type: {soil_type}
- Characteristics: {characteristics}

{_CONTROL_SENTENCE}

OUTPUT STRUCTURE (use these exact headings):
## Summary
(2–3 lines: what this soil type means for farming)

## Soil Condition
- Strengths
- Limitations to be aware of

## Best Crops
- Crops well-suited to this soil
- Why they perform well

## Improvement Tips
- How to improve soil health
- Practical steps

## Key Actions
- List 3–5 short, actionable items{lang_instruction}"""
    use_cache = (language or "en") == "en"
    ai_text, source = get_gemini_response(prompt, use_cache=use_cache, return_source=True)
    if not ai_text:
        fallback_text = build_soil_type_fallback(soil_type=soil_type, characteristics=characteristics, language=language)
        return (fallback_text, "fallback") if return_source else fallback_text
    return (ai_text, "ai") if return_source else ai_text


def generate_market_advisory(
    crop_name: str,
    trend: str,
    change_percent: float,
    latest_price: float,
    location: str = None,
    language: str = "en",
    return_source: bool = False,
):
    """Generate market advisory: price trend insight and action suggestions. UI-ready format."""
    lang_instruction = _lang_instruction(language)
    loc_str = f"Location: {location}" if location else ""
    prompt = f"""Generate a structured advisory for MARKET ADVISORY module.
{_FORMAT_RULES}

ANALYSIS DATA (use ONLY this — do not invent):
- Crop: {crop_name}
- Price Trend: {trend}
- Change: {change_percent}%
- Latest Price: ₹{latest_price}/quintal
{loc_str}

{_CONTROL_SENTENCE}

OUTPUT STRUCTURE (use these exact headings):
## Summary
(2–3 lines: price trend, current level, main implication)

## Price Insight
- What the trend indicates
- Typical factors affecting this crop

## Action Suggestions
- When to sell (if applicable)
- When to hold or wait
- Market timing tips

## Key Actions
- List 3-5 short, actionable items{lang_instruction}"""
    use_cache = (language or "en") == "en"
    ai_text, source = get_gemini_response(prompt, use_cache=use_cache, return_source=True)
    if not ai_text:
        fallback_text = build_market_fallback(crop_name=crop_name, trend=trend, change_percent=change_percent, latest_price=latest_price, location=location, language=language)
        return (fallback_text, "fallback") if return_source else fallback_text
    return (ai_text, "ai") if return_source else ai_text


def generate_interactive_advisory(
    query: str,
    location: str = "Vijayawada, Andhra Pradesh",
    crop_name: str = "Chilli",
    season: str = "Kharif",
    temperature: float = 28.0,
    weather_data: dict = None,
    soil_data: dict = None,
    market_data: dict = None,
    distress_score: int = None,
    user_id: int = None,
    language: str = "en",
    return_source: bool = True
):
    """Generate structured, actionable AI farm advisory for farmer queries with 5-section layout."""
    lang_instruction = _lang_instruction(language)
    weather_info = f"- Ambient Temperature: {temperature} C"
    if weather_data and isinstance(weather_data, dict):
        humidity = weather_data.get("humidity") or weather_data.get("main", {}).get("humidity")
        if humidity:
            weather_info += f", Relative Humidity: {humidity}%"

    prompt = f"""Generate a structured farmer advisory for AGRIDARSHAK DECISION SUPPORT platform.
{_FORMAT_RULES}

FARMER QUERY & CONTEXT:
- Farmer Question: {query}
- Farm Location: {location}
- Standing Crop: {crop_name}
- Agricultural Season: {season}
{weather_info}

{_CONTROL_SENTENCE}

OUTPUT STRUCTURE (use these exact headings):
## Situation & Agronomic Context
(2-3 lines: direct situation analysis based on the farmer question, crop, and location)

## Recommended Actions
1. (Specific actionable step with dosages if applicable)
2. (Specific preventive/management step)
3. (Field-tested biological or practical action)
4. (Actionable trap, cultivation, or grading measure)
5. (Follow-up observation timing)

## Why This Matters
(2-3 lines: agricultural root cause, moisture/weather mechanism, or economic reasoning)

## Priority Level
(TODAY or THIS WEEK or URGENT)

## Expected Benefit
(2-3 lines: concrete benefits, yield loss prevention %, input efficiency){lang_instruction}"""

    use_cache = (language or "en") == "en"
    ai_text, source = get_gemini_response(prompt, use_cache=use_cache, return_source=True)
    if not ai_text:
        fallback_text = build_interactive_advisory_fallback(
            query=query,
            location=location,
            crop_name=crop_name,
            weather_data=weather_data,
            soil_data=soil_data,
            market_data=market_data,
            distress_score=distress_score,
            language=language
        )
        return (fallback_text, "fallback") if return_source else fallback_text
    return (ai_text, "gemini") if return_source else ai_text


def clear_cache():
    global _response_cache
    _response_cache.clear()
    print("[OK] Cache cleared")


def get_cache_stats() -> dict:
    now = time.time()
    valid = sum(1 for _, (_, t) in _response_cache.items() if now - t < CACHE_DURATION_SEC)
    return {
        "total_cached": len(_response_cache),
        "valid_cached": valid,
        "cache_duration_sec": CACHE_DURATION_SEC,
    }
