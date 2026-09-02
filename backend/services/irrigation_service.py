"""
AgriDarshak Irrigation Scheduling Service
Generates data-driven irrigation advice based on crop growth stages, weather forecasts,
and soil characteristics, with farmer-friendly deterministic fallbacks.
"""
from typing import Dict, Any, Optional
from services.weather_service import weather_service


# Crop specific baseline water requirements (cm/week) and critical stages
CROP_WATER_GUIDELINES = {
    "rice": {"base_cm": 4.5, "critical_stage": "flowering", "moisture_type": "high"},
    "paddy": {"base_cm": 4.5, "critical_stage": "flowering", "moisture_type": "high"},
    "wheat": {"base_cm": 3.0, "critical_stage": "flowering", "moisture_type": "moderate"},
    "maize": {"base_cm": 3.5, "critical_stage": "flowering", "moisture_type": "moderate"},
    "corn": {"base_cm": 3.5, "critical_stage": "flowering", "moisture_type": "moderate"},
    "cotton": {"base_cm": 3.0, "critical_stage": "fruiting", "moisture_type": "deep"},
    "chilli": {"base_cm": 2.5, "critical_stage": "flowering", "moisture_type": "moderate"},
    "tomato": {"base_cm": 3.0, "critical_stage": "flowering", "moisture_type": "moderate"},
    "potato": {"base_cm": 3.0, "critical_stage": "fruiting", "moisture_type": "moderate"},
    "groundnut": {"base_cm": 2.5, "critical_stage": "flowering", "moisture_type": "moderate"},
    "sugarcane": {"base_cm": 5.0, "critical_stage": "vegetative", "moisture_type": "high"},
    "onion": {"base_cm": 2.5, "critical_stage": "fruiting", "moisture_type": "shallow"},
    "gram": {"base_cm": 2.0, "critical_stage": "flowering", "moisture_type": "low"},
    "chickpea": {"base_cm": 2.0, "critical_stage": "flowering", "moisture_type": "low"},
    "soybean": {"base_cm": 2.8, "critical_stage": "flowering", "moisture_type": "moderate"},
    "mustard": {"base_cm": 2.2, "critical_stage": "flowering", "moisture_type": "low"},
    "default": {"base_cm": 3.0, "critical_stage": "flowering", "moisture_type": "moderate"}
}

# Growth stage sensitivity multipliers
STAGE_WATER_FACTORS = {
    "seedling": {"factor": 0.6, "priority": "MEDIUM", "note": "Light, shallow irrigation to support tender root establishment without waterlogging."},
    "vegetative": {"factor": 1.0, "priority": "MEDIUM", "note": "Steady moisture replenishment to sustain rapid canopy and biomass development."},
    "flowering": {"factor": 1.4, "priority": "HIGH", "note": "Critical moisture-sensitive phase. Water stress now can cause floral abortion and irreversible yield loss."},
    "fruiting": {"factor": 1.2, "priority": "HIGH", "note": "Adequate water ensures optimal pod/fruit filling and uniform produce size."},
    "maturity": {"factor": 0.4, "priority": "LOW", "note": "Taper off irrigation to facilitate grain hardening, ripening, and field harvest readiness."}
}


def get_irrigation_recommendation(
    crop: str,
    growth_stage: str,
    location: str,
    soil_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate farmer-friendly irrigation schedule recommendation.
    Integrates live weather forecast, soil characteristics, and crop stage physiology.
    """
    crop_clean = (crop or "General Crop").strip().title()
    crop_key = crop_clean.lower()
    crop_info = CROP_WATER_GUIDELINES.get(crop_key, CROP_WATER_GUIDELINES["default"])

    stage_clean = (growth_stage or "vegetative").strip().lower()
    stage_info = STAGE_WATER_FACTORS.get(stage_clean, STAGE_WATER_FACTORS["vegetative"])

    loc = (location or "Vijayawada, Andhra Pradesh").strip()
    soil_clean = (soil_type or "").strip()

    # 1. Fetch live weather & forecast
    weather_data = None
    forecast_data = None
    has_weather = False
    has_rainfall = False
    has_temp = False
    has_humidity = False
    rain_next_48h = 0.0
    current_temp = 28.0
    current_humidity = 65

    try:
        weather_data = weather_service.get_current_weather(loc)
        if weather_data and "main" in weather_data:
            has_weather = True
            current_temp = weather_data["main"].get("temp", 28.0)
            current_humidity = weather_data["main"].get("humidity", 65)
            has_temp = True
            has_humidity = True

        forecast_data = weather_service.get_forecast(loc, days=3)
        if forecast_data and "list" in forecast_data and len(forecast_data["list"]) > 0:
            for item in forecast_data["list"][:2]:  # next 48h
                rain_mm = item.get("rain", {}).get("3h", 0.0) or 0.0
                rain_next_48h += rain_mm
            has_rainfall = True
    except Exception as e:
        print(f"[IRRIGATION] Weather lookup error: {e}")
        has_weather = False

    data_available = {
        "weather_forecast": has_weather and bool(forecast_data),
        "rainfall_forecast": has_rainfall,
        "soil_moisture": False,  # ALWAYS false unless physical telemetry hardware is connected
        "temperature": has_temp,
        "humidity": has_humidity
    }

    # 2. Evaluate Irrigation Window & Logic
    is_critical_stage = stage_clean == crop_info["critical_stage"] or stage_clean == "flowering"
    priority = "HIGH" if is_critical_stage else stage_info["priority"]

    # Soil guidance note
    soil_note = ""
    if soil_clean:
        s_lower = soil_clean.lower()
        if "sand" in s_lower:
            soil_note = f" In {soil_clean}, water percolates rapidly; opt for lighter, more frequent cycles."
        elif "clay" in s_lower or "black" in s_lower:
            soil_note = f" In {soil_clean}, water retention is high; avoid standing water to protect root aeration."
        else:
            soil_note = f" In {soil_clean}, maintain balanced moisture without saturation."
    else:
        soil_note = f" Soil type not recorded. Based on general {crop_clean} requirements, consider scheduling irrigation when the top 2 inches of soil feel dry."

    # Case A: Substantial Rain Predicted (> 5 mm in next 48 hours)
    if has_rainfall and rain_next_48h >= 5.0:
        recommendation_type = "forecast_based"
        next_window = "Delay irrigation for the next 48 hours"
        reason = f"Rainfall ({rain_next_48h:.1f} mm) is predicted across your area in the next 48 hours. Consider delaying scheduled irrigation to conserve water and prevent waterlogging.{soil_note}"
        priority = "LOW"
        expected_benefit = "Saves pumping diesel/electricity costs, avoids root asphyxiation, and prevents nitrogen leaching."
        weather_factor = f"Upcoming rain event predicted ({rain_next_48h:.1f} mm)."

    # Case B: High Heat & Evapotranspiration (> 33°C)
    elif has_weather and current_temp >= 33.0:
        recommendation_type = "forecast_based"
        next_window = "Tomorrow early morning, 6:00 AM - 8:30 AM"
        reason = f"Hot conditions ({current_temp:.1f}°C) lead to high surface evaporation. {stage_info['note']}{soil_note}"
        priority = "HIGH" if is_critical_stage else "MEDIUM"
        expected_benefit = "Early morning application minimizes evaporation loss by up to 35%, ensuring maximum water reaches the active root zone."
        weather_factor = f"Elevated temperature ({current_temp:.1f}°C) and dry air ({current_humidity}% humidity)."

    # Case C: Standard Stable Weather Forecast
    elif has_weather:
        recommendation_type = "forecast_based"
        next_window = "Tomorrow morning, 6:30 AM - 9:00 AM (or late evening)"
        reason = f"Favorable weather conditions ({current_temp:.1f}°C, {current_humidity}% humidity). {stage_info['note']}{soil_note}"
        priority = priority
        expected_benefit = "Maintains optimal soil-water tension, prevents blossom end rot, and sustains steady transpiration."
        weather_factor = f"Stable weather with normal daytime temperatures ({current_temp:.1f}°C) and no immediate rain threat."

    # Case D: Weather Unavailable -> General Agricultural Guidance
    else:
        recommendation_type = "general_guidance"
        next_window = "Early morning or late afternoon (standard 4-5 day cycle)"
        base_rate = crop_info["base_cm"] * stage_info["factor"]
        reason = f"We don't have current live weather data for your area. General guidance: {crop_clean} typically needs approximately {base_rate:.1f} cm water per week at {stage_clean} stage. Consider checking soil moisture manually.{soil_note}"
        priority = priority
        expected_benefit = "Protects against moisture deficit stress while preventing over-watering."
        weather_factor = "Live weather telemetry unavailable; standard agronomic baseline applied."

    return {
        "recommendation": {
            "current_crop": crop_clean,
            "next_window": next_window,
            "reason": reason,
            "priority": priority,
            "expected_benefit": expected_benefit,
            "weather_factor": weather_factor,
            "data_available": data_available,
            "recommendation_type": recommendation_type
        }
    }
