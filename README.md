# AgriDarshak — Farmer Distress Early-Warning & Agricultural Decision Support System (SIH 2026)

**AgriDarshak** is an integrated agricultural decision-support and early-warning platform designed for Indian farmers. Developed for the Smart India Hackathon (SIH 2026) prototype demonstration by the team from **NIT Rourkela, Odisha**. The system unifies real-time agro-meteorological alerts, APMC mandi price trends, quantitative soil NPK diagnostics, seasonal crop recommendations, and deep learning leaf pathology into a centralized, deterministic **Farm Health & Distress Risk Engine**.

---

## 1. Problem Statement

Smallholder farmers in India face compounding, simultaneous risks from erratic climate shifts, sudden crop pest outbreaks, volatile mandi price swings, and soil nutrient imbalances. Most existing digital agricultural tools operate in disconnected silos:
- Weather apps provide raw forecasts without agricultural impact context.
- Market tools list prices without correlating them to harvest readiness or distress indicators.
- Pathology tools diagnose leaf diseases without factoring in ambient climate risk or farm history.

When multiple stresses occur at once (e.g. pre-harvest heavy rainfall combined with local mandi price softening), farmers lack a single consolidated early-warning score that translates multi-source data into prioritized, actionable agronomic advice.

---

## 2. Proposed Solution

**AgriDarshak** addresses this challenge by combining disparate agronomic signals into a cohesive, farmer-centric dashboard:
1. **Farmer & Farm Context**: Stores land size, soil baseline history, location, and standing crop growth stages.
2. **Deterministic Farm Health / Distress Score ($0\text{--}100$)**: A multi-factor mathematical assessment weighting weather, disease susceptibility, market price trends, crop yield stages, soil fertility, and active context alerts.
3. **Dual-Tier Advisory Engine**:
   - **✨ AI Advisory**: Contextual recommendations powered by Google Gemini (using active production models `gemini-3.6-flash` / `gemini-3.5-flash`).
   - **🌱 Smart Advisory (Deterministic Local Fallback)**: Rule-based localized expert guidance based on real NPK values, disease diagnosis, weather risks, and mandi prices whenever Gemini is offline or rate-limited.
4. **Computer Vision Leaf Pathology**: On-device MobileNetV2 deep learning model diagnosing 38 plant conditions across 14 crop species.
5. **Full Multilingual & Voice Accessibility**: Localized interface support for 8 Indian languages: English, Odia, Hindi, Telugu, Tamil, Bengali, Gujarati, and Marathi, with Odia prioritized for the Odisha/NIT Rourkela demonstration.

---

## 3. Brand Identity & Logo Placement

- **Brand Name**: **AgriDarshak** (remains untranslated in all 8 languages as the definitive system brand name).
- **Brand Colors**:
  - Primary Green: `#1F7A45`
  - Secondary Leaf: `#5FAF45`
  - Harvest Gold Accent: `#D4A72C`
  - Soft Background: `#F7F9F4`
  - Forest Text: `#18322A`
  - Surface/Cards: `#FFFFFF`
- **Logo Asset**: The supplied AgriDarshak leaf logo is located at:
  ```
  frontend/public/agridarshak-logo.jpeg
  ```
  *(To replace or update the logo for official distribution, place the high-resolution logo image at `frontend/public/agridarshak-logo.jpeg`)*.

---

## 4. Key Features

- **8-Language Localization**: Complete interface and navigation localization across English, Odia, Hindi, Telugu, Tamil, Bengali, Gujarati, and Marathi with 414 canonical keys and zero raw string leaks.
- **Odia Farmer-Facing Support**: Authentic, localized agricultural vocabulary (ମାଟି/ମୃତ୍ତିକା, ପାଣିପାଗ, ମଣ୍ଡି ଦର, ରୋଗ ଚିହ୍ନଟ, ଫସଲ ସୁପାରିଶ, ବିପଦ ସୂଚକାଙ୍କ) and multi-tier voice Text-to-Speech (TTS) for the Odisha & NIT Rourkela demonstration.
- **Dynamic Farm Health Localization**: Risk factor explanations and recommended actions are dynamically translated using structured keys and localized parameter interpolation.
- **Localized AI Advisory**: Context-aware agronomic markdown guidance generated directly in the farmer's chosen language using Gemini active models.
- **Localized Deterministic Fallback Advisory**: Local rule-based advisory engine triggered automatically when offline or without API keys, providing real NPK, disease, weather, and mandi recommendations in all 8 languages.
- **Farm Health Centerpiece**: Live 0–100 score with LOW/MODERATE/HIGH/CRITICAL risk level derived from 6 transparent agronomic risk dimensions.

---

## 5. Supported Languages

The application provides end-to-end interface localization across 8 languages:

| Language | Code | Native Script | Brand Representation & Grounding |
| :--- | :---: | :---: | :--- |
| **English** | `en` | English | **AgriDarshak** • Master terminology |
| **Odia** | `or` | **ଓଡ଼ିଆ** | **AgriDarshak** • Native farmer-facing vocabulary (ମାଟି/ମୃତ୍ତିକା, ପାଣିପାଗ, ମଣ୍ଡି ଦର, ରୋଗ, ବିପଦ ସୂଚକାଙ୍କ) |
| **Hindi** | `hi` | हिन्दी | **AgriDarshak** • Complete agricultural translation |
| **Telugu** | `te` | తెలుగు | **AgriDarshak** • Complete agricultural translation |
| **Tamil** | `ta` | தமிழ் | **AgriDarshak** • Complete agricultural translation |
| **Bengali** | `bn` | বাংলা | **AgriDarshak** • Complete agricultural translation |
| **Gujarati** | `gu` | ગુજરાતી | **AgriDarshak** • Complete agricultural translation |
| **Marathi** | `mr` | मराठी | **AgriDarshak** • Complete agricultural translation |

---

## 6. Dual-Tier Advisory Architecture

The platform guarantees that farmers always receive actionable agronomic advice:

```
[ Farm Data Input (Soil NPK / Weather / Disease / Mandi / Language) ]
                               │
                               ▼
                [ Backend Advisory Controller ]
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
      [ Google Gemini API ]            [ Deterministic Local Fallback ]
      - Model: gemini-3.6-flash        - Activated if API key missing / offline
      - Model: gemini-3.5-flash        - Real application data driven:
      - Quota caching & rate limiting    * NPK / pH soil corrective doses
      - Direct multilingual output       * Bio-remediation & neem spray steps
              │                          * Agro-climatic crop matching
              │                          * Mandi rate momentum insight
              ▼                                 ▼
   [ "✨ AI Advisory" Badge ]         [ "🌱 Smart Advisory" Badge ]
              └────────────────┬────────────────┘
                               │
                               ▼
        [ Localized Markdown & Voice TTS in Browser ]
```

---

## 7. Technology Stack

- **Frontend**: React 18, Vite, React Router 6, Framer Motion, Axios, React Icons, i18next (Multilingual: en, or, hi, te, ta, bn, gu, mr), Web Speech API (Text-to-Speech).
- **Backend**: Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, Pydantic v2, SQLite (Local prototype DB).
- **Machine Learning & AI**: PyTorch, Torchvision, MobileNetV2 (38 plant disease classes), OpenCV / PIL for leaf validation, Google GenAI SDK (`google-genai`).
- **External Agro APIs**: Open-Meteo API (weather & climate geocoding), Data.gov.in / Agmarknet (mandi market rates).

---

## 8. Farm Health & Risk Calculation Engine

The distress score ($0\text{--}100$) is calculated **deterministically** on the backend:

$$\text{Distress Score} = \text{Weather (0--25)} + \text{Disease (0--20)} + \text{Market (0--20)} + \text{Crop/Yield (0--20)} + \text{Soil (0--10)} + \text{Context (0--5)}$$

### Risk Factor Weights:
- **Weather Risk (0–25)**: Evaluates 48-hour rainfall accumulation, extreme temperatures, and lodging wind speeds.
- **Disease Risk (0–20)**: Checks active disease alerts, standing crop status, and high humidity/warm temperature fungal predisposition.
- **Market Risk (0–20)**: Monitors APMC mandi 30-day price trajectories and flags sharp market crashes ($\le -12\%$).
- **Crop/Yield Risk (0–20)**: Evaluates standing crop maturity, harvest timing exposure, and irrigation intervals.
- **Soil Risk (0–10)**: Analyzes NPK balance, organic carbon rating, and soil pH extremes.
- **Context Risk (0–5)**: Flags unresolved critical alerts and farmer notification backlogs.

---

## 9. How to Run Locally

### Prerequisites
- Python 3.10+ (Python 3.11 / 3.12 / 3.14 compatible)
- Node.js 18+ and npm

### 1. Backend Setup
```bash
cd backend
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # On Windows (or source .venv/bin/activate on Linux/macOS)

# Install dependencies
pip install -r requirements.txt

# Run initial database setup
python init_database.py

# Start FastAPI server
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The application is accessible at:
- **Frontend App**: `http://localhost:5173`
- **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`

---

## 10. Gemini API Key Setup (For Live AI Demo)

1. Obtain a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Create a `.env` file in the project root directory (`SIH frontend/.env`):
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   DATABASE_URL=sqlite:///./crop_advisory.db
   SECRET_KEY=your-secret-key-change-in-production
   ```
3. Restart the backend server.
4. **Fallback Demonstration**: To test the deterministic fallback system during a demo, simply clear or remove `GEMINI_API_KEY` from `.env` and restart. The application will seamlessly serve **Smart Advisory** guidance with 0 disruption or generic failure errors.

---

## 11. Security Safeguards

- **Backend-Only Keys**: `GEMINI_API_KEY` is loaded strictly via backend server configuration and never exposed to the frontend browser bundle.
- **Git Protection**: `.env`, `.env.local`, and credential files are explicitly ignored in `.gitignore` and untracked in Git.
- **Safe Logging**: Backend logs record model invocation status without outputting secret tokens or authorization headers.

---

## 12. Automated Test Suite

Run the full automated test suite using the virtual environment:
```bash
cd backend
.venv\Scripts\python.exe test_ai_advisory.py     # AI Advisory & Deterministic Fallback tests
.venv\Scripts\python.exe test_farm_health.py     # Farm Health deterministic numerical score tests
.venv\Scripts\python.exe test_complete_flow.py   # End-to-end user and diagnostic workflow tests
```
