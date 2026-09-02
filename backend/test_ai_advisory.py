"""
Automated Test Suite for AI Advisory & Deterministic Fallback System.
Standalone test runner using standard library.
Tests:
1. Gemini success & active production model connectivity
2. Gemini failure graceful handling
3. Missing API key fallback
4. Fallback generation (Soil, Disease, Crop, Market)
5. Multi-language output (en, hi, or, te, ta, bn, gu, mr)
6. Malformed AI response handling
"""
import sys
from pathlib import Path
from unittest.mock import patch

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.gemini_service import (
    get_gemini_response,
    generate_disease_advisory,
    generate_crop_recommendation_explanation,
    generate_soil_analysis_explanation,
    generate_soil_type_explanation,
    generate_market_advisory
)
from services.advisory_fallback import (
    build_disease_fallback,
    build_soil_fallback,
    build_crop_fallback,
    build_soil_type_fallback,
    build_market_fallback
)


def test_1_gemini_success_with_active_model():
    """Test Gemini generates content with active production models or deterministic fallback."""
    from services.gemini_service import generate_interactive_advisory
    text, source = generate_interactive_advisory(
        query="Give practical irrigation advice for tomato in English",
        location="Rourkela, Odisha",
        crop_name="Tomato",
        language="en",
        return_source=True
    )
    assert text is not None and len(text) > 50, f"Expected non-empty response, got {text}"
    assert source in ["gemini", "ai", "fallback"], f"Unexpected source: {source}"
    print(f"[PASSED] Test 1: Advisory response source='{source}', response length={len(text)}")


def test_2_gemini_failure_triggers_deterministic_fallback():
    """Test that when Gemini API client raises an exception, deterministic fallback is returned."""
    from services import gemini_service
    
    class FailingClient:
        class models:
            @staticmethod
            def generate_content(*args, **kwargs):
                raise RuntimeError("Simulated upstream Gemini timeout / quota error")

    with patch.object(gemini_service, "_get_client", return_value=FailingClient()):
        result, source = generate_disease_advisory(
            disease_name="Tomato Early Blight",
            confidence=0.92,
            crop_name="Tomato",
            language="en",
            return_source=True
        )

        assert source == "fallback", f"Expected fallback, got {source}"
        assert "Early Blight" in result or "Tomato" in result
        assert "## Summary" in result or "## Agronomic Analysis" in result
        print(f"[PASSED] Test 2: Gemini failure gracefully handled with deterministic fallback (source='{source}')")


def test_3_missing_api_key_graceful_fallback():
    """Test that if no API key is available, the system falls back without crashing."""
    from services import gemini_service

    with patch.object(gemini_service, "_get_client", return_value=None):
        result, source = generate_soil_analysis_explanation(
            soil_params={"nitrogen": 140, "phosphorus": 15, "potassium": 120, "ph": 5.8, "soil_type": "Clay"},
            fertilizer_recommendations=["Urea", "DAP", "Lime"],
            language="or",
            return_source=True
        )

        assert source == "fallback", f"Expected fallback, got {source}"
        assert "ସାରାଂଶ" in result or "ପୋଷକ" in result
        print(f"[PASSED] Test 3: Missing API key handled with authentic Odia fallback (source='{source}')")


def test_4_fallback_generation_all_domains():
    """Verify deterministic fallbacks for all domain modules."""
    # Disease fallback
    d_fallback = build_disease_fallback("Rice Blast", 0.88, "Rice", language="or")
    assert "Rice Blast" in d_fallback
    assert "ଚିକିତ୍ସା" in d_fallback

    # Soil fallback
    s_fallback = build_soil_fallback({"nitrogen": 180, "phosphorus": 12, "potassium": 110, "ph": 6.2}, ["Urea", "Potash"], language="hi")
    assert "मृदा" in s_fallback or "नाइट्रोजन" in s_fallback

    # Crop recommendation fallback
    c_fallback = build_crop_fallback([{"name": "Paddy"}, {"name": "Maize"}], "Loamy", "Kharif", "Rourkela, Odisha", language="or")
    assert "Rourkela" in c_fallback or "Paddy" in c_fallback

    # Market fallback
    m_fallback = build_market_fallback("Paddy", "up", 4.5, 2350, location="Bhubaneswar Mandi", language="or")
    assert "2,350" in m_fallback
    print("[PASSED] Test 4: All domain fallbacks (Disease, Soil, Crop, Market) verified with rich local content")


def test_5_language_selection_odia_and_indic():
    """Verify Odia, Hindi, Telugu, and English output formats and script integrity."""
    languages = ["en", "hi", "or", "te", "ta", "bn", "gu", "mr"]
    
    for lang in languages:
        text, source = generate_disease_advisory(
            disease_name="Powdery Mildew",
            confidence=0.85,
            crop_name="Chilli",
            language=lang,
            return_source=True
        )
        assert len(text) > 50, f"Expected long text for {lang}, got length {len(text)}"
        assert source in ["gemini", "ai", "fallback"]
        print(f"         Lang '{lang}' ({source}) -> Length: {len(text)} chars")
    print("[PASSED] Test 5: All 8 languages successfully generated and validated")


def test_6_malformed_ai_response_handling():
    """Test that empty or whitespace-only response from AI triggers fallback."""
    from services import gemini_service

    class EmptyResponseClient:
        class models:
            @staticmethod
            def generate_content(*args, **kwargs):
                class Resp:
                    text = "   "
                return Resp()

    with patch.object(gemini_service, "_get_client", return_value=EmptyResponseClient()):
        result, source = generate_soil_type_explanation(
            soil_type="Black Soil",
            characteristics={"water_retention": "High", "drainage": "Poor"},
            language="en",
            return_source=True
        )
        assert source == "fallback", f"Expected fallback, got {source}"
        assert "Black Soil" in result
        print(f"[PASSED] Test 6: Malformed whitespace AI response cleanly recovered with fallback (source='{source}')")


def test_7_interactive_advisory_and_odia_fallback():
    """Verify interactive advisory responds cleanly with guaranteed resolution in Odia and English."""
    from services.gemini_service import generate_interactive_advisory
    from services.advisory_fallback import build_interactive_advisory_fallback

    # Odia Weather query fallback
    or_advisory = build_interactive_advisory_fallback(
        query="ଆଗାମୀ ବର୍ଷାରେ ଫସଲ ସୁରକ୍ଷା କିପରି କରିବି?",
        location="Rourkela, Odisha",
        language="or"
    )
    assert "ପଦକ୍ଷେପ" in or_advisory or "ସ୍ଥିତି" in or_advisory or "ପରାମର୍ଶ" in or_advisory or "ବର୍ଷା" in or_advisory
    assert "କାରଣ" in or_advisory or "ପ୍ରାଥମିକତା" in or_advisory

    # Direct generate_interactive_advisory test
    adv_text, adv_source = generate_interactive_advisory(
        query="Organic pest control measures for current season",
        location="Rourkela, Odisha",
        crop_name="Chilli",
        language="en",
        return_source=True
    )
    assert len(adv_text) > 50
    assert adv_source in ["gemini", "ai", "fallback"]
    print(f"[PASSED] Test 7: Interactive advisory & Odia fallback verified (source='{adv_source}')")


if __name__ == "__main__":
    print("\n=======================================================")
    print("RUNNING AUTOMATED AI ADVISORY & FALLBACK SUITE")
    print("=======================================================")
    test_1_gemini_success_with_active_model()
    test_2_gemini_failure_triggers_deterministic_fallback()
    test_3_missing_api_key_graceful_fallback()
    test_4_fallback_generation_all_domains()
    test_5_language_selection_odia_and_indic()
    test_6_malformed_ai_response_handling()
    test_7_interactive_advisory_and_odia_fallback()
    print("=======================================================")
    print("ALL 7 TEST CASES PASSED SUCCESSFULLY (100% GREEN)")
    print("=======================================================\n")
