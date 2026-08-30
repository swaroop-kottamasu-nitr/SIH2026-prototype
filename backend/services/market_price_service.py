"""
Market price service - All Indian states.
Season and location aware crop prices. Uses data.gov.in API when key is set.
"""
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import get_settings

settings = get_settings()

# Default state: Andhra Pradesh
DEFAULT_STATE = "Andhra Pradesh"

# Load states and cities from JSON (all Indian states with mandi cities)
_STATES_CITIES: Dict[str, List[str]] = {}
_LOCATION_TO_STATE: Dict[str, str] = {}

def _load_states_cities() -> Dict[str, List[str]]:
    """Load states and cities from india_states_cities.json."""
    global _STATES_CITIES, _LOCATION_TO_STATE
    if _STATES_CITIES:
        return _STATES_CITIES
    data_file = Path(__file__).parent.parent / "data" / "india_states_cities.json"
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            _STATES_CITIES = json.load(f)
        # Build city -> state lookup
        for state, cities in _STATES_CITIES.items():
            _LOCATION_TO_STATE[state.lower()] = state
            for city in cities:
                _LOCATION_TO_STATE[city.lower()] = state
        return _STATES_CITIES
    except Exception:
        _STATES_CITIES = {"Andhra Pradesh": ["Vijayawada", "Guntur", "Visakhapatnam", "Kurnool", "Nellore"]}
        return _STATES_CITIES


def get_all_states() -> List[str]:
    """Return list of all Indian states/UTs with market data."""
    data = _load_states_cities()
    return sorted(data.keys())


def get_cities_for_state(state: str) -> List[str]:
    """Return list of cities/mandis for a given state."""
    data = _load_states_cities()
    return data.get(state, [])


# AP-specific mandis (for fallback when state is Andhra Pradesh)
AP_MARKETS = [
    "Guntur Chilli Yard", "Vijayawada Rythu Bazar", "Kurnool APMC", "Rajahmundry Mandi",
    "Visakhapatnam Market", "Tirupati APMC", "Nellore Mandi", "Kakinada Port Market",
    "Anantapur APMC", "Eluru Rythu Bazar", "Ongole Groundnut Yard",
]


def _get_markets_for_state(state: str) -> List[str]:
    """Get mandi/market names for fallback prices in a state."""
    if state == "Andhra Pradesh":
        return AP_MARKETS
    cities = get_cities_for_state(state)
    if cities:
        return [f"{c} APMC" for c in cities[:8]] + [f"{c} Mandi" for c in cities[:4]]
    return ["APMC Market", "Mandi", "Rythu Bazar", "Local Market"]

# India crop seasons by month (1=Jan, 2=Feb, ...)
# Kharif: Jun-Oct (6-10), Rabi: Nov-Mar (11,12,1,2,3), Summer: Apr-May (4,5)
def get_current_season() -> str:
    m = datetime.now().month
    if 6 <= m <= 10:
        return "Kharif"
    if m in (11, 12, 1, 2, 3):
        return "Rabi"
    return "Summer"


def _resolve_state(location: str) -> str:
    """Resolve user location (city/state) to state name. Default: Andhra Pradesh."""
    if not location or not location.strip():
        return DEFAULT_STATE
    _load_states_cities()  # Ensure lookup is built
    loc = location.strip().lower()
    if loc in _LOCATION_TO_STATE:
        return _LOCATION_TO_STATE[loc]
    for city, state in _LOCATION_TO_STATE.items():
        if city in loc or loc in city:
            return state
    # Check if it's already a state from our list
    for state in get_all_states():
        if state.lower() == loc or state.lower() in loc or loc in state.lower():
            return state
    return DEFAULT_STATE


def get_season_crops_for_location(location: str) -> List[Dict]:
    """Get crops suitable for current season and user's location from crops.json."""
    state = _resolve_state(location)
    season = get_current_season()

    crops_file = Path(__file__).parent.parent / "data" / "crops.json"
    try:
        with open(crops_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            crops = data.get("crops", [])
    except Exception:
        return []

    result = []
    for c in crops:
        seasons = c.get("seasons", [])
        states = c.get("states", [])
        if (season in seasons or "Year-round" in seasons) and (
            state in states or not states
        ):
            result.append({
                "name": c["name"],
                "local_name": c.get("local_name", ""),
                "season": season,
                "states": states,
            })
    return result


# Realistic price ranges (₹/quintal) - Andhra Pradesh market rates
# AP is major producer of: Chilli (Guntur), Rice, Groundnut, Cotton, Tobacco
CROP_BASE_PRICES = {
    "Rice": (1800, 3200), "Wheat": (2000, 2800), "Cotton": (5500, 7500),
    "Groundnut": (4500, 6500), "Sugarcane": (300, 350), "Maize": (1800, 2400),
    "Pulses (Tur)": (8000, 12000), "Jowar (Sorghum)": (1800, 2200),
    "Pearl Millet (Bajra)": (1500, 2200), "Tomato": (800, 4000),
    "Potato": (800, 1800), "Onion": (1000, 3500),
    "Chilli": (12000, 22000), "Tobacco": (8000, 15000), "Turmeric": (6000, 12000),
}


def _fetch_from_datagov(commodity: str, state: str) -> Optional[List[Dict]]:
    """Fetch from data.gov.in API if key is set."""
    api_key = getattr(settings, "data_gov_in_api_key", None) or ""
    if not api_key or api_key == "your_datagov_key":
        return None
    try:
        # Resource ID for agricultural prices (may need update)
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0060"
        params = {
            "api-key": api_key,
            "format": "json",
            "limit": 50,
            "filters[state]": state,
            "filters[commodity]": commodity,
        }
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        records = data.get("records", [])
        if not records:
            return None
        out = []
        for rec in records[:20]:
            pr = rec.get("modal_price") or rec.get("max_price") or rec.get("min_price")
            if pr:
                try:
                    price = float(pr)
                except (TypeError, ValueError):
                    continue
                out.append({
                    "state": rec.get("state", state),
                    "market": rec.get("market", "Mandi"),
                    "price": price,
                    "date": rec.get("date", datetime.now().date().isoformat()),
                })
        return out if out else None
    except Exception as e:
        print(f"Market price API error: {e}")
        return None


def _generate_fallback_prices(crop_name: str, state: str) -> List[Dict]:
    """Generate realistic fallback prices when API unavailable."""
    base_range = CROP_BASE_PRICES.get(crop_name, (1500, 3000))
    markets = _get_markets_for_state(state)
    prices = []
    import random
    for i in range(30):
        date = datetime.now().date() - timedelta(days=i)
        base = (base_range[0] + base_range[1]) / 2
        var = random.uniform(-0.15, 0.15)
        price = round(base * (1 + var), 2)
        prices.append({
            "state": state,
            "market": random.choice(markets),
            "price": price,
            "date": date.isoformat(),
        })
    return prices


def get_season_prices_for_location(
    location: str,
) -> Dict:
    """
    Get market prices for season crops in user's location.
    Returns dict with crops array, each with name, prices, trend, etc.
    """
    state = _resolve_state(location)
    season = get_current_season()
    crops = get_season_crops_for_location(location)

    if not crops:
        # Fallback to popular crops
        crops = [{"name": n} for n in ["Rice", "Wheat", "Potato", "Onion", "Tomato"]]

    result = {
        "location": location,
        "state": state,
        "season": season,
        "crops": [],
    }

    for c in crops[:8]:  # Max 8 crops
        name = c["name"]
        api_prices = _fetch_from_datagov(name, state)
        if api_prices:
            price_list = api_prices
        else:
            price_list = _generate_fallback_prices(name, state)

        if not price_list:
            continue

        latest = price_list[0]["price"]
        older = price_list[-1]["price"] if len(price_list) > 1 else latest
        trend = "up" if latest > older else "down" if latest < older else "stable"
        change = ((latest - older) / older * 100) if older > 0 else 0

        result["crops"].append({
            "crop_name": name,
            "latest_price": latest,
            "trend": trend,
            "change_percent": round(change, 2),
            "prices": price_list[:10],
            "prices_count": len(price_list),
        })

    return result


def get_crop_prices_for_location(
    crop_name: str,
    location: str,
    days: int = 30,
) -> Dict:
    """Get prices for a specific crop in user's location."""
    state = _resolve_state(location)
    api_prices = _fetch_from_datagov(crop_name, state)
    if api_prices:
        price_list = api_prices
    else:
        price_list = _generate_fallback_prices(crop_name, state)

    if not price_list:
        return {"crop_name": crop_name, "prices": [], "latest_price": None, "trend": "stable", "change_percent": 0}

    latest = price_list[0]["price"]
    older = price_list[-1]["price"] if len(price_list) > 1 else latest
    trend = "up" if latest > older else "down" if latest < older else "stable"
    change = ((latest - older) / older * 100) if older > 0 else 0

    return {
        "crop_name": crop_name,
        "prices": [
            {"state": p["state"], "market": p["market"], "price": p["price"], "date": p["date"]}
            for p in price_list[:20]
        ],
        "count": len(price_list),
        "trend": trend,
        "change_percent": round(change, 2),
        "latest_price": latest,
    }
