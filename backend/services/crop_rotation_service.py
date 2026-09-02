"""
AgriDarshak Crop Rotation Planning Service
Provides deterministic, agronomy-backed crop rotation recommendations
to break pest/pathogen life cycles, restore soil nutrient balance, and enhance yields.
"""
from typing import List, Dict, Any, Optional

# Botanical family groupings and soil properties
CROP_AGRONOMY_DATA = {
    "rice": {
        "family": "Poaceae",
        "type": "Cereal",
        "root_depth": "Shallow (0-40 cm)",
        "nutrient_demand": "Heavy Nitrogen & Potassium consumer",
        "next_season_recommendations": {
            "rabi": ["Chickpea", "Mustard", "Wheat", "Lentil", "Groundnut"],
            "summer": ["Green Gram (Moong)", "Black Gram (Urad)", "Sesame", "Cowpea"],
            "kharif": ["Paddy", "Soybean", "Maize"]
        }
    },
    "paddy": {
        "family": "Poaceae",
        "type": "Cereal",
        "root_depth": "Shallow (0-40 cm)",
        "nutrient_demand": "Heavy Nitrogen & Potassium consumer",
        "next_season_recommendations": {
            "rabi": ["Chickpea", "Mustard", "Wheat", "Lentil", "Groundnut"],
            "summer": ["Green Gram (Moong)", "Black Gram (Urad)", "Sesame"],
            "kharif": ["Soybean", "Maize", "Cotton"]
        }
    },
    "wheat": {
        "family": "Poaceae",
        "type": "Cereal",
        "root_depth": "Medium (40-80 cm)",
        "nutrient_demand": "Moderate-Heavy consumer",
        "next_season_recommendations": {
            "summer": ["Green Gram (Moong)", "Cowpea", "Sesame", "Groundnut"],
            "kharif": ["Soybean", "Rice", "Maize", "Cotton", "Pigeon Pea (Arhar)"],
            "rabi": ["Chickpea", "Mustard"]
        }
    },
    "cotton": {
        "family": "Malvaceae",
        "type": "Cash / Deep Root",
        "root_depth": "Deep Taproot (100-150 cm)",
        "nutrient_demand": "High Potassium & Boron consumer",
        "next_season_recommendations": {
            "rabi": ["Wheat", "Chickpea", "Mustard", "Barley"],
            "summer": ["Green Gram (Moong)", "Fodder Sorghum"],
            "kharif": ["Soybean", "Maize", "Groundnut"]
        }
    },
    "chilli": {
        "family": "Solanaceae",
        "type": "Solanaceous Vegetable",
        "root_depth": "Medium (50-70 cm)",
        "nutrient_demand": "High Potash & Phosphorus requirement",
        "next_season_recommendations": {
            "rabi": ["Garlic", "Onion", "Gram", "Wheat"],
            "summer": ["Green Gram (Moong)", "Cowpea", "Cluster Bean (Guar)"],
            "kharif": ["Maize", "Groundnut", "Soybean", "Paddy"]
        }
    },
    "tomato": {
        "family": "Solanaceae",
        "type": "Solanaceous Vegetable",
        "root_depth": "Medium (50-70 cm)",
        "nutrient_demand": "Heavy Calcium & Potash feeder",
        "next_season_recommendations": {
            "rabi": ["Garlic", "French Beans", "Wheat", "Mustard"],
            "summer": ["Green Gram (Moong)", "Okra", "Cowpea"],
            "kharif": ["Maize", "Soybean", "Groundnut", "Rice"]
        }
    },
    "potato": {
        "family": "Solanaceae",
        "type": "Tuber Vegetable",
        "root_depth": "Shallow (30-50 cm)",
        "nutrient_demand": "High Potash & Nitrogen feeder",
        "next_season_recommendations": {
            "summer": ["Green Gram (Moong)", "Sesame", "Maize (fodder)"],
            "kharif": ["Paddy", "Soybean", "Maize", "Sesame"],
            "rabi": ["Wheat", "Mustard"]
        }
    },
    "maize": {
        "family": "Poaceae",
        "type": "Cereal",
        "root_depth": "Medium-Deep (60-100 cm)",
        "nutrient_demand": "Heavy feeder",
        "next_season_recommendations": {
            "rabi": ["Chickpea", "Mustard", "Potato", "Wheat"],
            "summer": ["Green Gram (Moong)", "Cowpea", "Sesame"],
            "kharif": ["Soybean", "Groundnut", "Pigeon Pea (Arhar)"]
        }
    },
    "sugarcane": {
        "family": "Poaceae",
        "type": "Long Duration Perennial",
        "root_depth": "Deep (100-150 cm)",
        "nutrient_demand": "Very High Nitrogen & Organic depletion",
        "next_season_recommendations": {
            "rabi": ["Wheat", "Chickpea", "Mustard"],
            "summer": ["Green Gram (Moong)", "Sunhemp (Green Manure)"],
            "kharif": ["Paddy", "Soybean", "Cotton"]
        }
    },
    "groundnut": {
        "family": "Fabaceae",
        "type": "Legume / Oilseed",
        "root_depth": "Medium (40-60 cm)",
        "nutrient_demand": "Nitrogen fixer, High Calcium requirement",
        "next_season_recommendations": {
            "rabi": ["Wheat", "Mustard", "Barley", "Sunflower"],
            "summer": ["Sesame", "Fodder Maize"],
            "kharif": ["Cotton", "Paddy", "Maize", "Sorghum"]
        }
    },
    "soybean": {
        "family": "Fabaceae",
        "type": "Legume / Oilseed",
        "root_depth": "Medium (40-60 cm)",
        "nutrient_demand": "Biological Nitrogen Fixer",
        "next_season_recommendations": {
            "rabi": ["Wheat", "Chickpea", "Mustard", "Garlic"],
            "summer": ["Green Gram (Moong)", "Sesame"],
            "kharif": ["Cotton", "Maize", "Paddy"]
        }
    },
    "chickpea": {
        "family": "Fabaceae",
        "type": "Pulse / Legume",
        "root_depth": "Deep Taproot (80-120 cm)",
        "nutrient_demand": "Biological Nitrogen Fixer, low fertilizer need",
        "next_season_recommendations": {
            "summer": ["Green Gram (Moong)", "Sesame", "Cowpea"],
            "kharif": ["Cotton", "Paddy", "Maize", "Soybean", "Bajra"],
            "rabi": ["Wheat", "Mustard"]
        }
    }
}

# Detailed agronomic rotation profiles for target crops
ROTATION_TARGET_PROFILES = {
    "Chickpea": {
        "soil_benefit": "Symbiotic Rhizobium root nodules fix 35–45 kg atmospheric Nitrogen per hectare, enriching residual soil fertility for subsequent cereal crops.",
        "pest_break_benefit": "Breaks the continuous lifecycle of cereal leaf blights, soil-borne nematodes, and stem borers.",
        "season": ["rabi"],
        "best_after": ["Rice", "Paddy", "Maize", "Cotton", "Sorghum", "Chilli"]
    },
    "Green Gram (Moong)": {
        "soil_benefit": "Short-duration (60–65 days) legume adds high-quality green biomass and 30 kg/ha organic nitrogen, improving soil water retention.",
        "pest_break_benefit": "Breaks weed cycles and soil-borne fungal pathogens between major cropping seasons.",
        "season": ["summer", "kharif"],
        "best_after": ["Wheat", "Potato", "Mustard", "Rice", "Sugarcane"]
    },
    "Black Gram (Urad)": {
        "soil_benefit": "Dense canopy suppresses weed emergence and enriches topsoil organic carbon content through leaf litter drop.",
        "pest_break_benefit": "Interrupts bacterial wilt and viral disease vectors common in continuous monocultures.",
        "season": ["summer", "kharif"],
        "best_after": ["Rice", "Wheat", "Maize", "Chilli"]
    },
    "Mustard": {
        "soil_benefit": "Deep root penetration loosens plough pans and releases bio-fumigating glucosinolate compounds in root exudates.",
        "pest_break_benefit": "Naturally suppresses root-knot nematodes and soil-borne fungal sclerotia (Rhizoctonia/Fusarium).",
        "season": ["rabi"],
        "best_after": ["Rice", "Cotton", "Maize", "Soybean", "Tomato"]
    },
    "Wheat": {
        "soil_benefit": "Extensive fibrous root network binds aggregate soil particles, improving structure after leguminous crops.",
        "pest_break_benefit": "Breaks cotton bollworm and tobacco caterpillar life cycles.",
        "season": ["rabi"],
        "best_after": ["Soybean", "Groundnut", "Cotton", "Rice", "Pigeon Pea (Arhar)"]
    },
    "Soybean": {
        "soil_benefit": "High nitrogen fixation and deep taproot improve subsoil porosity and organic matter content.",
        "pest_break_benefit": "Breaks the disease cycle of cereal rusts and root rot complexes.",
        "season": ["kharif"],
        "best_after": ["Wheat", "Mustard", "Potato", "Garlic"]
    },
    "Pigeon Pea (Arhar)": {
        "soil_benefit": "Extremely deep taproots (up to 2 meters) break dense subsoil hardpans and scavenge subsoil phosphorus and calcium.",
        "pest_break_benefit": "Breaks shallow soil pest cycles and provides long-term field soil aeration.",
        "season": ["kharif"],
        "best_after": ["Wheat", "Rice", "Mustard", "Cotton"]
    },
    "Groundnut": {
        "soil_benefit": "Supplies residual soil nitrogen and calcium recycling; ideal for sandy loam and alluvial soils.",
        "pest_break_benefit": "Breaks solanaceous bacterial wilt and fungal blight complexes.",
        "season": ["kharif", "rabi", "summer"],
        "best_after": ["Cotton", "Maize", "Rice", "Wheat"]
    },
    "Maize": {
        "soil_benefit": "High biomass residue enriches soil humus; strong root architecture improves soil drainage.",
        "pest_break_benefit": "Non-host break crop for Solanaceous bacterial wilt and root-knot nematodes.",
        "season": ["kharif", "rabi"],
        "best_after": ["Chilli", "Tomato", "Potato", "Chickpea", "Groundnut"]
    },
    "Garlic": {
        "soil_benefit": "Sulfur-rich root exudates reduce soil fungal pathogen loads.",
        "pest_break_benefit": "Repels sucking insect vectors and suppresses soil nematodes.",
        "season": ["rabi"],
        "best_after": ["Chilli", "Tomato", "Soybean", "Maize"]
    }
}


def get_crop_rotation_recommendations(
    previous_crop: str,
    season: str,
    current_crop: Optional[str] = None,
    soil_type: Optional[str] = None,
    crop_history: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate agronomic crop rotation recommendations.
    Uses crop history and soil context when available, falling back to generalized agronomic rotation rules.
    """
    prev_clean = (previous_crop or "Rice").strip().title()
    prev_key = prev_clean.lower()
    
    season_clean = (season or "rabi").strip().lower()
    if "summer" in season_clean or "zaid" in season_clean:
        target_season = "summer"
    elif "rabi" in season_clean:
        target_season = "rabi"
    else:
        target_season = "kharif"

    has_history = bool(crop_history and len(crop_history) > 0)
    data_source = "history_based" if has_history else "generalized"
    confidence = "HIGH" if has_history else "LOW"

    # Soil type context note
    soil_clean = (soil_type or "").strip()
    soil_is_estimate = not bool(soil_clean)

    # 1. Lookup agronomy data for previous crop
    prev_info = CROP_AGRONOMY_DATA.get(prev_key, CROP_AGRONOMY_DATA.get("rice"))
    candidate_names = prev_info["next_season_recommendations"].get(target_season, ["Chickpea", "Green Gram (Moong)", "Mustard", "Wheat"])

    # If crop history exists, avoid crops planted in the last 2 cycles to enforce diversity
    if has_history:
        recent_crops_lower = [c.strip().lower() for c in crop_history[-3:] if c]
        # Filter candidate names that were recently grown
        filtered = [c for c in candidate_names if c.lower() not in recent_crops_lower]
        if filtered:
            candidate_names = filtered

    recommendations = []

    for name in candidate_names[:4]:
        profile = ROTATION_TARGET_PROFILES.get(name, {
            "soil_benefit": "Restores soil macro-nutrient balance and enhances organic carbon.",
            "pest_break_benefit": "Breaks the continuous lifecycle of seasonal crop-specific pests.",
            "season": [target_season],
            "best_after": [prev_clean]
        })

        # Calculate seasonal suitability
        suitability = "HIGH" if target_season in profile.get("season", [target_season]) else "MEDIUM"

        # Tailor soil benefit based on soil_type if available
        soil_benefit = profile["soil_benefit"]
        if soil_is_estimate:
            soil_benefit = f"Soil benefit estimate based on crop family ({prev_info['family']} -> {name}): {soil_benefit}"
        elif "black" in soil_clean.lower() or "clay" in soil_clean.lower():
            soil_benefit += f" In {soil_clean}, its taproots significantly improve subsoil aeration and drainage."
        elif "sand" in soil_clean.lower():
            soil_benefit += f" In {soil_clean}, root biomass enhances soil moisture retention and organic matter."

        # Construct specific agronomic reasoning
        reason = f"Following {prev_clean} ({prev_info['family']}), planting {name} restores soil nutrient balance after {prev_info['nutrient_demand'].lower()} and prevents pest build-up."

        recommendations.append({
            "crop": name,
            "reason": reason,
            "soil_benefit": soil_benefit,
            "pest_break_benefit": profile["pest_break_benefit"],
            "season_suitability": suitability,
            "confidence": confidence
        })

    # Ensure at least 2 recommendations
    if not recommendations:
        recommendations = [
            {
                "crop": "Chickpea",
                "reason": f"Ideal nitrogen-fixing pulse following {prev_clean} to rejuvenate soil fertility.",
                "soil_benefit": "Adds 35-40 kg N/ha biological nitrogen and improves soil structure.",
                "pest_break_benefit": "Breaks fungal and pest lifecycles of the preceding crop.",
                "season_suitability": "HIGH",
                "confidence": confidence
            },
            {
                "crop": "Green Gram (Moong)",
                "reason": f"Short duration legume provides quick turnaround and high biomass addition after {prev_clean}.",
                "soil_benefit": "Fixes atmospheric nitrogen and enriches topsoil organic matter.",
                "pest_break_benefit": "Suppresses soil-borne pathogens and root-knot nematodes.",
                "season_suitability": "HIGH",
                "confidence": confidence
            }
        ]

    return {
        "recommendations": recommendations,
        "data_source": data_source
    }
