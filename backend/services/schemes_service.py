"""
AgriDarshak Government Welfare Schemes Demo Service
Provides structured directory of central and state agricultural support initiatives
and estimated eligibility matching for Indian farmers.
"""
from typing import Dict, Any, List, Optional

DEMO_SCHEMES = [
    {
        "id": "SCH_PMKISAN",
        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "description": "Direct income support of ₹6,000 per year in three equal installments of ₹2,000 directly into the bank accounts of landholding farmer families.",
        "category": "subsidy",
        "eligibility": "All landholding farmer families with cultivable landholding in their names, subject to statutory exclusion criteria.",
        "benefits": "₹6,000/year direct financial assistance for procuring agricultural inputs and domestic needs.",
        "deadline": "2026-12-31",
        "application_link": "https://pmkisan.gov.in",
        "data_source": "demo"
    },
    {
        "id": "SCH_PMFBY",
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "description": "Comprehensive yield-based crop insurance coverage against non-preventable natural risks from pre-sowing to post-harvest stages.",
        "category": "insurance",
        "eligibility": "All farmers growing notified crops in notified areas (both loanee and non-loanee farmers).",
        "benefits": "Nominal premium rates (2% Kharif food/oilseeds, 1.5% Rabi food/oilseeds, 5% annual commercial/horticultural crops) with full claim settlement for losses.",
        "deadline": "2026-07-31",
        "application_link": "https://pmfby.gov.in",
        "data_source": "demo"
    },
    {
        "id": "SCH_KCC",
        "name": "Kisan Credit Card (KCC) Scheme",
        "description": "Timely and affordable institutional credit for cultivation, post-harvest expenses, farm asset maintenance, and allied agricultural activities.",
        "category": "loan",
        "eligibility": "Individual/joint cultivators, tenant farmers, oral lessees, and sharecroppers.",
        "benefits": "Short-term crop loans up to ₹3,00,000 at a subsidized interest rate of 4% per annum upon prompt repayment.",
        "deadline": "2026-12-31",
        "application_link": "https://agricoop.nic.in",
        "data_source": "demo"
    },
    {
        "id": "SCH_SHC",
        "name": "Soil Health Card (SHC) Scheme",
        "description": "Periodic soil nutrient assessment card issued to farmers containing status of 12 critical nutrients and dosage recommendations.",
        "category": "training",
        "eligibility": "All landholders and cultivating farmers across India.",
        "benefits": "Free or nominal soil sampling testing with customized fertilizer and micronutrient advisory to reduce input costs.",
        "deadline": "2026-12-31",
        "application_link": "https://soilhealth.dac.gov.in",
        "data_source": "demo"
    },
    {
        "id": "SCH_NMSA",
        "name": "National Mission on Sustainable Agriculture (NMSA)",
        "description": "Promotion of organic farming, soil health management, on-farm water management, and climate-resilient farming techniques.",
        "category": "training",
        "eligibility": "Small and marginal farmers, farmer producer organizations (FPOs), and village clusters.",
        "benefits": "Financial subsidies for micro-irrigation installations, bio-fertilizer units, and vermicompost pits up to 50%.",
        "deadline": "2026-09-30",
        "application_link": "https://nmsa.dac.gov.in",
        "data_source": "demo"
    },
    {
        "id": "SCH_ENAM",
        "name": "National Agriculture Market (e-NAM)",
        "description": "Pan-India electronic trading portal networking existing APMC mandis to create a unified national market for agricultural commodities.",
        "category": "other",
        "eligibility": "All registered farmers possessing land records or trader identity with an active bank account.",
        "benefits": "Transparent online bidding, real-time price discovery, access to nationwide buyers, and direct online payment.",
        "deadline": "2026-12-31",
        "application_link": "https://enam.gov.in",
        "data_source": "demo"
    },
    {
        "id": "SCH_AGRICLINIC",
        "name": "Agri-Clinics and Agri-Business Centres (ACABC)",
        "description": "Expert services, farm clinics, custom hiring centres, and input supply setups for modern agricultural practices.",
        "category": "loan",
        "eligibility": "Agricultural graduates, diploma holders in agriculture, and trained progressive farmers.",
        "benefits": "Composite loan up to ₹20 lakhs with back-ended capital subsidy (36% to 44%) through NABARD.",
        "deadline": "2026-12-31",
        "application_link": "https://acabcmis.gov.in",
        "data_source": "demo"
    }
]

def get_all_schemes(category: Optional[str] = None) -> Dict[str, Any]:
    """
    Return all government schemes with optional category filtering.
    """
    cat_clean = (category or "").strip().lower()
    if not cat_clean or cat_clean == "all":
        schemes = list(DEMO_SCHEMES)
    else:
        schemes = [s for s in DEMO_SCHEMES if s["category"] == cat_clean]

    return {
        "schemes": schemes,
        "disclaimer": "This is demonstration data for SIH 2026. Verify all scheme details with official government sources."
    }

def estimate_scheme_eligibility(
    crop: Optional[str] = None,
    location: Optional[str] = None,
    farm_size: Optional[float] = None
) -> Dict[str, Any]:
    """
    Estimate eligible schemes based on basic farm profile parameters.
    """
    crop_clean = (crop or "Rice").strip().title()
    size = float(farm_size or 2.5)

    eligible = []

    # PM-KISAN
    eligible.append({
        "scheme_id": "SCH_PMKISAN",
        "match_reason": f"Applicable for cultivating landholders with active farm profile in {location or 'India'}.",
        "confidence": "HIGH"
    })

    # PMFBY
    eligible.append({
        "scheme_id": "SCH_PMFBY",
        "match_reason": f"{crop_clean} is a notified crop eligible for comprehensive yield & weather risk coverage.",
        "confidence": "HIGH"
    })

    # KCC
    eligible.append({
        "scheme_id": "SCH_KCC",
        "match_reason": f"Eligible for subsidized short-term working capital loans for {size} acre {crop_clean} cultivation.",
        "confidence": "HIGH"
    })

    # NMSA if small/marginal (< 5 acres)
    if size <= 5.0:
        eligible.append({
            "scheme_id": "SCH_NMSA",
            "match_reason": "Qualifies for small/marginal farmer subsidy benefits on micro-irrigation and organic inputs.",
            "confidence": "MEDIUM"
        })

    # Soil Health Card
    eligible.append({
        "scheme_id": "SCH_SHC",
        "match_reason": "Eligible for free periodic soil test card and customized NPK advisories.",
        "confidence": "HIGH"
    })

    return {
        "eligible_schemes": eligible,
        "disclaimer": "Eligibility is estimated based on sample data. Verify with official sources."
    }
