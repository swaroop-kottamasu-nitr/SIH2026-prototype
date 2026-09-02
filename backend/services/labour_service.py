"""
AgriDarshak Agricultural Labour Booking Demo Service
Demonstrates rural farm labour discovery and task allocation
with clear disclaimers and synthetic data for SIH 2026.
"""
from typing import Dict, Any, List, Optional
import uuid

DEMO_WORKERS = [
    {
        "id": "wrk_101",
        "name": "Balaram Sahoo & Team",
        "skills": ["harvesting", "planting", "weeding"],
        "daily_wage": 450,
        "location": "Kisan Nagar, Rourkela Block",
        "availability": "available",
        "rating": 4.8,
        "data_source": "demo"
    },
    {
        "id": "wrk_102",
        "name": "Rameshwar Goud (Spraying Specialist)",
        "skills": ["pesticide", "fertilizer"],
        "daily_wage": 550,
        "location": "Guntur Rural, Ward 4",
        "availability": "available",
        "rating": 4.9,
        "data_source": "demo"
    },
    {
        "id": "wrk_103",
        "name": "Sita Devi Women Farm Collective",
        "skills": ["weeding", "transplanting", "harvesting"],
        "daily_wage": 400,
        "location": "Sundargarh East",
        "availability": "available",
        "rating": 4.7,
        "data_source": "demo"
    },
    {
        "id": "wrk_104",
        "name": "Kishan Lal (Micro-Irrigation Tech)",
        "skills": ["irrigation", "equipment"],
        "daily_wage": 500,
        "location": "Vijayawada Outer Ring",
        "availability": "limited",
        "rating": 4.6,
        "data_source": "demo"
    },
    {
        "id": "wrk_105",
        "name": "Pratap Jena Harvester Crew",
        "skills": ["harvesting", "threshing"],
        "daily_wage": 600,
        "location": "Sambalpur Canal Road",
        "availability": "available",
        "rating": 4.9,
        "data_source": "demo"
    },
    {
        "id": "wrk_106",
        "name": "Maheshwara Reddy",
        "skills": ["fertilizer", "irrigation", "weeding"],
        "daily_wage": 420,
        "location": "Kurnool Sub-Division",
        "availability": "available",
        "rating": 4.5,
        "data_source": "demo"
    },
    {
        "id": "wrk_107",
        "name": "Anand Nayak (Tractor & Plough Operator)",
        "skills": ["planting", "equipment"],
        "daily_wage": 580,
        "location": "Panposh Sector",
        "availability": "limited",
        "rating": 4.8,
        "data_source": "demo"
    },
    {
        "id": "wrk_108",
        "name": "Lakshmi Narayana Agri Laborers",
        "skills": ["harvesting", "pesticide", "irrigation"],
        "daily_wage": 480,
        "location": "Tenali Rural",
        "availability": "available",
        "rating": 4.7,
        "data_source": "demo"
    }
]

def get_available_labour(skill: Optional[str] = None) -> Dict[str, Any]:
    """
    Return list of available workers, optionally filtered by skill.
    """
    skill_clean = (skill or "").strip().lower()
    
    if not skill_clean or skill_clean == "all":
        workers = list(DEMO_WORKERS)
    else:
        workers = [
            w for w in DEMO_WORKERS 
            if skill_clean in [s.lower() for s in w["skills"]]
        ]
        
    return {
        "workers": workers,
        "disclaimer": "This is demonstration data. Actual labour availability may vary."
    }

def create_labour_booking_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a demo labour booking request.
    """
    req_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
    return {
        "request_id": req_id,
        "status": "pending",
        "message": f"Demo booking request {req_id} registered successfully.",
        "demo_notice": "This is a demo booking request. No actual worker has been contacted."
    }
