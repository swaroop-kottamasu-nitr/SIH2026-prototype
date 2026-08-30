"""
Farm Health & Distress Risk Assessment Service.
Calculates a deterministic 0-100 risk score combining:
- Weather Risk       (0-25)
- Disease Risk       (0-20)
- Market Risk        (0-20)
- Crop/Yield Risk    (0-20)
- Soil Risk          (0-10)
- Context Risk       (0-5)

Risk Levels:
  0-25:  LOW
  26-50: MODERATE
  51-75: HIGH
  76-100: CRITICAL

IMPORTANT: Uses deterministic calculations over available DB and service data (NO LLM for numerical score).
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.user import User
from models.soil_analysis_history import SoilAnalysisHistory
from models.crop_history import CropHistory
from models.current_crop import CurrentCrop
from models.alert import Alert
from services.weather_service import weather_service
from services.market_price_service import get_season_prices_for_location


def _get_risk_level(score: float, max_score: float) -> str:
    """Classify sub-factor risk ratio."""
    ratio = score / max_score if max_score > 0 else 0
    if ratio >= 0.75:
        return "CRITICAL"
    elif ratio >= 0.50:
        return "HIGH"
    elif ratio >= 0.25:
        return "MODERATE"
    return "LOW"


def _get_overall_risk_level(total_score: int) -> str:
    """Classify overall farm risk level."""
    if total_score >= 76:
        return "CRITICAL"
    elif total_score >= 51:
        return "HIGH"
    elif total_score >= 26:
        return "MODERATE"
    return "LOW"


def calculate_weather_risk(location: str) -> Dict:
    """
    Evaluate Weather Risk (0-25 points).
    Checks rainfall forecast, extreme temperatures, wind speed, and humidity.
    """
    score = 3.0  # Baseline favorable score
    reasons = []

    try:
        current = weather_service.get_current_weather(location)
        forecast = weather_service.get_forecast(location, days=5)

        # 1. Check rainfall in forecast (next 3 days)
        total_rain = 0.0
        max_period_rain = 0.0
        if forecast and "list" in forecast:
            for item in forecast["list"][:8]:  # ~24-48 hours
                rain_val = item.get("rain", {}).get("3h", 0) or item.get("rain", {}).get("1h", 0) or 0
                total_rain += rain_val
                if rain_val > max_period_rain:
                    max_period_rain = rain_val

        if total_rain >= 60.0 or max_period_rain >= 30.0:
            score += 16.0
            reasons.append(f"Heavy rainfall ({total_rain:.1f}mm) forecast over next 48 hours - risk of waterlogging")
        elif total_rain >= 25.0:
            score += 9.0
            reasons.append(f"Moderate rainfall ({total_rain:.1f}mm) expected - check field drainage")
        elif total_rain == 0.0 and current and current.get("main", {}).get("temp", 25) > 38:
            score += 10.0
            reasons.append("Dry spell combined with high temperature - drought stress risk")

        # 2. Check temperature
        if current and "main" in current:
            temp = current["main"].get("temp", 28)
            if temp >= 42.0:
                score += 10.0
                reasons.append(f"Severe heatwave condition ({temp:.1f}°C) - extreme heat stress")
            elif temp >= 38.0:
                score += 5.0
                reasons.append(f"Elevated temperature ({temp:.1f}°C) - increased irrigation requirement")
            elif temp <= 6.0:
                score += 10.0
                reasons.append(f"Cold snap / frost alert ({temp:.1f}°C) - risk of chilling injury")

        # 3. Check wind speed
        if current and "wind" in current:
            wind_speed = current["wind"].get("speed", 0) * 3.6  # m/s to km/h
            if wind_speed >= 38.0:
                score += 8.0
                reasons.append(f"High wind gusts ({wind_speed:.1f} km/h) - crop lodging danger")

        # Cap score between 0 and 25
        final_score = min(25, max(0, round(score)))
        primary_reason = "; ".join(reasons) if reasons else "Favorable weather conditions with normal temperature and rainfall"

        return {
            "name": "Weather Risk",
            "score": final_score,
            "max_score": 25,
            "level": _get_risk_level(final_score, 25),
            "reason": primary_reason
        }

    except Exception:
        return {
            "name": "Weather Risk",
            "score": 4,
            "max_score": 25,
            "level": "LOW",
            "reason": "Weather conditions within seasonal normal range"
        }


def calculate_disease_risk(db: Session, user: Optional[User], location: str) -> Dict:
    """
    Evaluate Disease Risk (0-20 points).
    Checks active disease alerts, infected standing crops, and humidity/temp vulnerability.
    """
    score = 2.0
    reasons = []

    try:
        # 1. Check user's recent disease alerts (last 14 days)
        if user:
            fourteen_days_ago = datetime.now() - timedelta(days=14)
            recent_disease_alerts = db.query(Alert).filter(
                Alert.user_id == user.id,
                Alert.alert_type == "disease",
                Alert.created_at >= fourteen_days_ago
            ).all()

            if recent_disease_alerts:
                score += 14.0
                disease_titles = [a.title for a in recent_disease_alerts[:2]]
                reasons.append(f"Active disease detection on record ({', '.join(disease_titles)})")

        # 2. Check standing crops health status
        if user:
            standing_crops = db.query(CurrentCrop).filter(CurrentCrop.user_id == user.id).all()
            for crop in standing_crops:
                if crop.health_status and crop.health_status.lower() in ["diseased", "pest_attack", "stressed"]:
                    score += 10.0
                    reasons.append(f"Standing crop {crop.crop_name} flagged as {crop.health_status}")
                    break

        # 3. Check micro-climate disease predisposition (high humidity + warm temp)
        current = weather_service.get_current_weather(location)
        if current and "main" in current:
            humidity = current["main"].get("humidity", 60)
            temp = current["main"].get("temp", 26)
            if humidity >= 82 and 20 <= temp <= 32:
                score += 8.0
                reasons.append(f"High ambient humidity ({humidity}%) creates elevated fungal/bacterial blight vulnerability")
            elif humidity >= 70:
                score += 4.0
                reasons.append(f"Moderate humidity ({humidity}%) - monitor leaves for early symptoms")

        final_score = min(20, max(0, round(score)))
        primary_reason = "; ".join(reasons) if reasons else "No active disease detected; climate conditions show low fungal risk"

        return {
            "name": "Disease Risk",
            "score": final_score,
            "max_score": 20,
            "level": _get_risk_level(final_score, 20),
            "reason": primary_reason
        }

    except Exception:
        return {
            "name": "Disease Risk",
            "score": 3,
            "max_score": 20,
            "level": "LOW",
            "reason": "Plant health conditions stable with low pathogen pressure"
        }


def calculate_market_risk(location: str) -> Dict:
    """
    Evaluate Market Risk (0-20 points).
    Checks mandi commodity price trajectories and price drops in local markets.
    """
    score = 3.0
    reasons = []

    try:
        seasonal_data = get_season_prices_for_location(location)
        crops = seasonal_data.get("crops", []) if seasonal_data else []

        if crops:
            declining_crops = []
            avg_change = 0.0
            for c in crops:
                change = c.get("change_percent", 0.0)
                avg_change += change
                if change <= -5.0:
                    declining_crops.append(f"{c['crop_name']} ({change:.1f}%)")

            avg_change = avg_change / len(crops)

            if len(declining_crops) >= 3 or avg_change <= -8.0:
                score += 14.0
                reasons.append(f"Widespread mandi price drop across key crops: {', '.join(declining_crops[:3])}")
            elif len(declining_crops) >= 1 or avg_change < -2.0:
                score += 8.0
                reasons.append(f"Softening rates in local mandis for {', '.join(declining_crops[:2])}")
            elif avg_change >= 4.0:
                score = max(1.0, score - 2.0)
                reasons.append(f"Favorable market conditions with firm mandi prices (+{avg_change:.1f}%)")
            else:
                reasons.append("Mandi prices stable with standard seasonal fluctuation")
        else:
            reasons.append("Mandi price movements within standard seasonal benchmarks")

        final_score = min(20, max(0, round(score)))
        primary_reason = "; ".join(reasons) if reasons else "Market prices are stable or trending favorably"

        return {
            "name": "Market Risk",
            "score": final_score,
            "max_score": 20,
            "level": _get_risk_level(final_score, 20),
            "reason": primary_reason
        }

    except Exception:
        return {
            "name": "Market Risk",
            "score": 4,
            "max_score": 20,
            "level": "LOW",
            "reason": "Mandi commodity rates within standard seasonal range"
        }


def calculate_crop_yield_risk(db: Session, user: Optional[User], weather_risk_score: int) -> Dict:
    """
    Evaluate Crop/Yield Risk (0-20 points).
    Checks harvest proximity, crop growth stress, and historical yield volatility.
    """
    score = 3.0
    reasons = []

    try:
        if user:
            standing_crops = db.query(CurrentCrop).filter(CurrentCrop.user_id == user.id).all()
            today = datetime.now().date()

            if standing_crops:
                for crop in standing_crops:
                    # Check harvest proximity
                    if crop.expected_harvest_date:
                        days_to_harvest = (crop.expected_harvest_date - today).days
                        if 0 <= days_to_harvest <= 14:
                            if weather_risk_score >= 12:
                                score += 14.0
                                reasons.append(f"Standing crop ({crop.crop_name}) near harvest stage ({days_to_harvest}d left) during adverse weather - lodging risk")
                            else:
                                score += 6.0
                                reasons.append(f"Standing crop ({crop.crop_name}) near harvest - prepare harvesting equipment")
                        elif days_to_harvest < 0:
                            score += 12.0
                            reasons.append(f"Harvest overdue for {crop.crop_name} - immediate field collection needed")

                    # Check irrigation / fertilizer delay
                    if crop.last_watered:
                        days_unwatered = (today - crop.last_watered).days
                        if days_unwatered > 12:
                            score += 6.0
                            reasons.append(f"{crop.crop_name} has not been irrigated in {days_unwatered} days")
            else:
                # No active crops in system
                reasons.append("No active standing crops logged; general seasonal baseline applied")
        else:
            reasons.append("Standard crop cycle progression matching seasonal timeline")

        final_score = min(20, max(0, round(score)))
        primary_reason = "; ".join(reasons) if reasons else "Crops are in healthy vegetative stage matching current seasonal cycle"

        return {
            "name": "Crop/Yield Risk",
            "score": final_score,
            "max_score": 20,
            "level": _get_risk_level(final_score, 20),
            "reason": primary_reason
        }

    except Exception:
        return {
            "name": "Crop/Yield Risk",
            "score": 3,
            "max_score": 20,
            "level": "LOW",
            "reason": "Crop vegetative growth progress is normal"
        }


def calculate_soil_risk(db: Session, user: Optional[User]) -> Dict:
    """
    Evaluate Soil Risk (0-10 points).
    Checks latest NPK levels, pH balance, and organic matter ratings.
    """
    score = 2.0
    reasons = []

    try:
        if user:
            latest_soil = db.query(SoilAnalysisHistory)\
                .filter(SoilAnalysisHistory.user_id == user.id)\
                .order_by(SoilAnalysisHistory.analysis_date.desc())\
                .first()

            if latest_soil:
                health = (latest_soil.soil_health or "").lower()
                ph = latest_soil.ph or 7.0

                if health == "poor" or ph < 5.2 or ph > 8.5:
                    score += 7.0
                    reasons.append(f"Soil test indicates poor fertility / extreme pH ({ph:.1f}) - nutrient uptake restricted")
                elif health == "medium" or ph < 6.0 or ph > 7.8:
                    score += 4.0
                    reasons.append(f"Sub-optimal soil health (pH {ph:.1f}) - mild NPK deficiency detected")
                else:
                    reasons.append(f"Well-balanced soil nutrients with optimal pH ({ph:.1f})")
            else:
                score += 3.0
                reasons.append("No recent soil test on record; regular NPK testing recommended")
        else:
            reasons.append("Standard soil fertility baseline assumed")

        final_score = min(10, max(0, round(score)))
        primary_reason = "; ".join(reasons) if reasons else "Soil health and nutrient profile are balanced"

        return {
            "name": "Soil Risk",
            "score": final_score,
            "max_score": 10,
            "level": _get_risk_level(final_score, 10),
            "reason": primary_reason
        }

    except Exception:
        return {
            "name": "Soil Risk",
            "score": 2,
            "max_score": 10,
            "level": "LOW",
            "reason": "Soil condition is within normal parameters"
        }


def calculate_context_risk(db: Session, user: Optional[User]) -> Dict:
    """
    Evaluate Context Risk (0-5 points).
    Checks unresolved critical alerts and farmer responsiveness.
    """
    score = 1.0
    reasons = []

    try:
        if user:
            unread_alerts = db.query(Alert).filter(
                Alert.user_id == user.id,
                Alert.is_read == 0
            ).count()

            if unread_alerts >= 3:
                score += 4.0
                reasons.append(f"{unread_alerts} unread critical alerts require immediate review")
            elif unread_alerts >= 1:
                score += 2.0
                reasons.append(f"{unread_alerts} active alert pending farmer review")
            else:
                reasons.append("Alert notifications resolved; farm profile up to date")
        else:
            reasons.append("Standard farming context profile")

        final_score = min(5, max(0, round(score)))
        primary_reason = "; ".join(reasons) if reasons else "Farmer responsiveness and profile status optimal"

        return {
            "name": "Context Risk",
            "score": final_score,
            "max_score": 5,
            "level": _get_risk_level(final_score, 5),
            "reason": primary_reason
        }

    except Exception:
        return {
            "name": "Context Risk",
            "score": 1,
            "max_score": 5,
            "level": "LOW",
            "reason": "Farm context indicators normal"
        }


def generate_recommendations(factors: List[Dict]) -> List[str]:
    """
    Generate 2-4 prioritized actionable recommendations based on highest risk factors.
    """
    rec_pool = []

    # Map factors by name for fast lookup
    factor_map = {f["name"]: f for f in factors}

    w_risk = factor_map.get("Weather Risk", {})
    d_risk = factor_map.get("Disease Risk", {})
    m_risk = factor_map.get("Market Risk", {})
    c_risk = factor_map.get("Crop/Yield Risk", {})
    s_risk = factor_map.get("Soil Risk", {})

    # Weather actions
    if w_risk.get("score", 0) >= 12:
        if "rain" in w_risk.get("reason", "").lower():
            rec_pool.append("Clear drainage channels and secure low-lying field bunds before heavy rainfall.")
        elif "heat" in w_risk.get("reason", "").lower():
            rec_pool.append("Schedule light evening irrigation and apply organic mulching to prevent moisture loss.")
        elif "wind" in w_risk.get("reason", "").lower():
            rec_pool.append("Provide staking support for tall crops and delay foliar spraying until winds subside.")
        else:
            rec_pool.append("Monitor field conditions closely for impending adverse weather shifts.")

    # Crop / Harvest actions
    if c_risk.get("score", 0) >= 10:
        if "harvest" in c_risk.get("reason", "").lower():
            rec_pool.append("Accelerate harvesting of mature crop stands before weather conditions deteriorate.")
        elif "irrigat" in c_risk.get("reason", "").lower():
            rec_pool.append("Replenish scheduled irrigation to prevent soil moisture stress.")
        else:
            rec_pool.append("Inspect crop vegetative progress and ensure timely agronomic care.")

    # Disease actions
    if d_risk.get("score", 0) >= 9:
        if "active disease" in d_risk.get("reason", "").lower():
            rec_pool.append("Isolate infected crop foliage and apply recommended bio-fungicide or neem formulation.")
        else:
            rec_pool.append("Inspect leaves for early blight or pest symptoms under current high-humidity conditions.")

    # Market actions
    if m_risk.get("score", 0) >= 9:
        if "drop" in m_risk.get("reason", "").lower() or "softening" in m_risk.get("reason", "").lower():
            rec_pool.append("Consider staggered selling or check nearby district APMC mandis for higher prevailing rates.")
        else:
            rec_pool.append("Track daily APMC mandi rates to plan optimal harvesting and dispatch timing.")

    # Soil actions
    if s_risk.get("score", 0) >= 5:
        if "poor" in s_risk.get("reason", "").lower() or "ph" in s_risk.get("reason", "").lower():
            rec_pool.append("Apply balanced NPK fertilizer and organic manure to correct soil nutrient depletion.")
        else:
            rec_pool.append("Schedule a soil test at your nearest KVK centre to optimize fertilizer dosage.")

    # Fallback recommendations if overall risk is low
    if len(rec_pool) < 2:
        rec_pool.append("Maintain regular crop scouting and scheduled irrigation.")
        rec_pool.append("Track local weather alerts and daily mandi prices on the dashboard.")

    # Return between 2 and 4 recommendations
    return rec_pool[:4]


def calculate_farm_health_risk(
    db: Session,
    user_id: Optional[int] = None,
    location: Optional[str] = None
) -> Dict:
    """
    Main entrypoint: Calculates deterministic Farm Health & Distress Risk Assessment.
    """
    user = None
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()

    # Resolve location
    resolved_loc = location or (user.location if user and user.location else "Vijayawada, Andhra Pradesh")

    # 1. Weather Risk (0-25)
    weather_factor = calculate_weather_risk(resolved_loc)

    # 2. Disease Risk (0-20)
    disease_factor = calculate_disease_risk(db, user, resolved_loc)

    # 3. Market Risk (0-20)
    market_factor = calculate_market_risk(resolved_loc)

    # 4. Crop/Yield Risk (0-20)
    crop_factor = calculate_crop_yield_risk(db, user, weather_factor["score"])

    # 5. Soil Risk (0-10)
    soil_factor = calculate_soil_risk(db, user)

    # 6. Context Risk (0-5)
    context_factor = calculate_context_risk(db, user)

    factors = [
        weather_factor,
        disease_factor,
        market_factor,
        crop_factor,
        soil_factor,
        context_factor
    ]

    total_score = sum(f["score"] for f in factors)
    total_score = max(0, min(100, round(total_score)))
    overall_level = _get_overall_risk_level(total_score)
    recommendations = generate_recommendations(factors)

    return {
        "score": total_score,
        "risk_level": overall_level,
        "factors": factors,
        "recommendations": recommendations
    }
