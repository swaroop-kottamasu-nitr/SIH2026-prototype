"""
AgriDarshak Post-Harvest Storage Locator Service
Locates nearby state warehousing godowns, cold chain facilities,
and rural grain silos to protect harvested commodities from spoilage and distress selling.
"""
from typing import Dict, Any, List, Optional

SAMPLE_STORAGE_FACILITIES = [
    {
        "name": "State Warehousing Corporation (SWC) Central Godown",
        "type": "Warehouse",
        "location": "Mandi Industrial Area, Gate 2",
        "capacity": "15,000 Metric Tonnes",
        "contact": "+91 866 245 8891",
        "distance": 6.5,
        "capacity_known": True,
        "availability_confirmed": False
    },
    {
        "name": "Central Warehousing Corporation (CWC) Scientific Silos",
        "type": "Silo",
        "location": "Railway Siding Yard, Sector 4",
        "capacity": "25,000 Metric Tonnes",
        "contact": "+91 866 257 1120",
        "distance": 11.0,
        "capacity_known": True,
        "availability_confirmed": False
    },
    {
        "name": "Kisan Multi-Chamber Fruit & Vegetable Cold Storage",
        "type": "Cold Storage",
        "location": "NH-16 Bypass, Cold Chain Park",
        "capacity": "5,000 MT (Controlled Atmosphere)",
        "contact": "+91 98481 99023",
        "distance": 8.2,
        "capacity_known": True,
        "availability_confirmed": False
    },
    {
        "name": "Guntur Agri-Logistics Chilli Cold Chain",
        "type": "Cold Storage",
        "location": "Chilli Board Complex, Autonagar",
        "capacity": "8,000 MT",
        "contact": "+91 863 229 4431",
        "distance": 18.5,
        "capacity_known": True,
        "availability_confirmed": False
    },
    {
        "name": "Primary Agricultural Cooperative (PACS) Rural Godown",
        "type": "Godown",
        "location": "Block Agricultural Center, Village Link Road",
        "capacity": "Not specified",
        "contact": "+91 94403 55210",
        "distance": 4.2,
        "capacity_known": False,
        "availability_confirmed": False
    },
    {
        "name": "APMC Yard Covered Storage Shed",
        "type": "Warehouse",
        "location": "Main APMC Terminal, Shed 3",
        "capacity": "Not specified",
        "contact": "+91 866 230 1900",
        "distance": 3.5,
        "capacity_known": False,
        "availability_confirmed": False
    }
]

def search_storage_facilities(
    crop: Optional[str] = None,
    quantity: Optional[float] = None,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search storage and cold chain facilities for crop preservation.
    """
    crop_clean = (crop or "General").strip().title()
    loc_clean = (location or "Vijayawada, Andhra Pradesh").strip()
    city = loc_clean.split(",")[0].strip()

    facilities = []
    for fac in SAMPLE_STORAGE_FACILITIES:
        item = dict(fac)
        item["location"] = f"{item['location']}, {city}"
        facilities.append(item)

    # Sort by distance
    facilities.sort(key=lambda x: x["distance"])

    return {
        "facilities": facilities,
        "data_source": "demo"  # Labeled clearly as sample/demo directory
    }
