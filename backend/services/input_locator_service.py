"""
AgriDarshak Agricultural Input Locator Service
Enables farmers to locate nearby suppliers of certified seeds, organic fertilizers,
crop protection inputs, and farm machinery/drip equipment.
"""
from typing import Dict, Any, List, Optional
from services.market_price_service import _resolve_state

SAMPLE_INPUT_DEALERS = [
    {
        "name": "Kisan Seva Kendra & Seed Corporation",
        "category": "seeds",
        "address": "Opp. Main Market Yard, Trunk Road",
        "contact": "+91 94401 23891",
        "distance": 3.8,
        "data_verified": True
    },
    {
        "name": "Rythu Bharosa Agro Infoline & Seeds",
        "category": "seeds",
        "address": "Near Block Agricultural Office, Bus Stand Road",
        "contact": "+91 98480 56712",
        "distance": 6.2,
        "data_verified": True
    },
    {
        "name": "IFFCO / KRIBHCO Farmers Fertilizer Hub",
        "category": "fertilizers",
        "address": "Primary Agricultural Cooperative Society (PACS) Compound",
        "contact": "+91 91210 44556",
        "distance": 4.5,
        "data_verified": True
    },
    {
        "name": "Sri Venkateswara Bio-Fertilizers & Nutrients",
        "category": "fertilizers",
        "address": "Industrial Estate, Godown Road",
        "contact": "+91 94902 78120",
        "distance": 8.0,
        "data_verified": False
    },
    {
        "name": "Annapurna IPM & Botanical Pest Controls",
        "category": "pesticides",
        "address": "Shop No. 12, APMC Complex",
        "contact": "+91 98661 11244",
        "distance": 5.1,
        "data_verified": False
    },
    {
        "name": "Krishi Raksha Certified Agro Chemicals",
        "category": "pesticides",
        "address": "Mandi Highway Cross, Shop 4",
        "contact": "+91 94412 88901",
        "distance": 9.4,
        "data_verified": True
    },
    {
        "name": "Jain & Netafim Micro-Irrigation & Farm Machinery",
        "category": "equipment",
        "address": "Plot 45, Bypass Service Road",
        "contact": "+91 99890 33411",
        "distance": 7.3,
        "data_verified": True
    },
    {
        "name": "Kisan Custom Hiring Centre (Tractors & Harvesters)",
        "category": "equipment",
        "address": "Gram Panchayat Bhawan Ground",
        "contact": "+91 97011 44523",
        "distance": 11.2,
        "data_verified": True
    },
    {
        "name": "Green Gold Certified Horticultural Nursery",
        "category": "other",
        "address": "National Highway 65, Km Stone 14",
        "contact": "+91 98492 67800",
        "distance": 14.0,
        "data_verified": False
    },
    {
        "name": "Adarsh Soil Testing & Bio-Input Distribution Unit",
        "category": "other",
        "address": "Krishi Vigyan Kendra (KVK) Campus",
        "contact": "+91 94405 12903",
        "distance": 12.5,
        "data_verified": True
    }
]

def search_agricultural_inputs(
    category: Optional[str] = None,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search agricultural input dealers by category and location.
    """
    cat_clean = (category or "all").strip().lower()
    loc_clean = (location or "Vijayawada, Andhra Pradesh").strip()
    
    city = loc_clean.split(",")[0].strip()

    filtered = []
    for item in SAMPLE_INPUT_DEALERS:
        if cat_clean == "all" or not cat_clean or item["category"] == cat_clean:
            item_copy = dict(item)
            item_copy["address"] = f"{item_copy['address']}, {city}"
            filtered.append(item_copy)

    # Sort by distance
    filtered.sort(key=lambda x: x["distance"])

    return {
        "results": filtered,
        "data_source": "demo"  # Labeled clearly as sample/demo directory
    }
