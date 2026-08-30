# Smart Crop Advisory & Farmer Distress Early-Warning System (SIH 2026)

An integrated agricultural decision-support and early-warning platform designed for Indian farmers. The system unifies real-time weather alerts, APMC mandi price trends, soil NPK analysis, crop recommendation, and computer vision plant pathology into a deterministic **Farm Health & Distress Risk Engine**.

---

## 1. Problem Statement

Smallholder farmers in India face compounding risks from erratic weather events, sudden crop disease outbreaks, fluctuating mandi market prices, and soil nutrient depletion. Most existing agricultural digital tools operate in silos:
- Weather apps show raw forecasts without agricultural impact context.
- Market tools list prices without correlating them to harvest readiness or distress indicators.
- Pathology tools diagnose leaf diseases without factoring in ambient climate risk or farm history.

When multiple stresses occur simultaneously (e.g., pre-harvest heavy rainfall combined with an APMC price crash), farmers lack a single consolidated early-warning score that translates multi-source data into prioritized, actionable steps.

---

## 2. Proposed Solution

The **Smart Crop Advisory & Farmer Distress Early-Warning System** addresses this challenge by combining disparate agronomic signals into a cohesive, farmer-centric dashboard:
1. **Farmer & Farm Context**: Stores land size, soil baseline history, and standing crop growth stages.
2. **Deterministic Farm Health / Distress Score ($0\text{--}100$)**: A multi-factor mathematical assessment weighting weather, disease susceptibility, market price trends, crop yield stages, soil fertility, and active context alerts.
3. **Actionable Agronomic Guidance**: Converts detected risk factors into prioritized, human-readable recommendations without hallucinations.
4. **Computer Vision Leaf Pathology**: On-device MobileNetV2 deep learning model diagnosing 38 plant conditions across 14 crop species.
5. **Multilingual Accessibility**: Localized interface support for Telugu, Tamil, Hindi, and English.

---

## 3. Key Features

- **🛡️ Deterministic Farm Health Centerpiece**:
  - Live numerical risk rating ($0\text{--}100$) categorized into `LOW`, `MODERATE`, `HIGH`, or `CRITICAL`.
  - Directional risk trend indicator (`Risk increasing ↑`, `Risk stable →`, `Risk low & stable ↓`).
  - Structured **Attention** list detailing specific vulnerabilities (🌧️ Weather, 🐛 Disease, 📉 Market, 🌾 Crop, 🌱 Soil).
  - Prioritized **Recommended Actions** with verified agronomic steps.
- **🌤️ Live Weather Pulse & Climate Alerts**:
  - Real-time temperature, humidity, wind velocity, and 5-day agro-meteorological forecasts via Open-Meteo.
  - Automated threshold alerts for heavy precipitation ($>60\text{mm}$), heatwaves ($>40^\circ\text{C}$), and frost.
- **📈 APMC Mandi Market Intelligence**:
  - Real-time commodity market tracking across Andhra Pradesh district mandis (Guntur, Vijayawada, Kurnool, etc.).
  - 30-day directional price movement trends and seasonal profitability insights.
- **🧪 Soil NPK & Fertility Analysis**:
  - Quantitative N, P, K evaluation with pH classification (Acidic, Neutral, Alkaline).
  - Fertilizer dosage recommendations based on baseline crop requirements.
- **⚡ Multi-Factor Crop Recommendation Engine**:
  - Rule-based agronomic filtering cross-referencing soil type, seasonal calendar (Kharif, Rabi, Zaid), and local temperature.
- **🔬 AI Leaf Disease Detection**:
  - PyTorch MobileNetV2 model pre-trained on the PlantVillage benchmark.
  - Image quality and leaf presence pre-filtering to avoid erroneous predictions on non-crop images.

---

## 4. Technology Stack

- **Frontend**: React 18, Vite, React Router 6, Framer Motion, Axios, React Icons, i18next (Multilingual: en, te, ta, hi).
- **Backend**: Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, Pydantic v2, SQLite (Local prototype DB).
- **Machine Learning & AI**: PyTorch, Torchvision, MobileNetV2 (38 plant disease classes), OpenCV / PIL for image processing, Google GenAI SDK (for contextual agronomic explanations).
- **External Agro APIs**: Open-Meteo API (weather & climate geocoding), Data.gov.in / Agmarknet (mandi market rates).

---

## 5. System Architecture

```
[ Web & Mobile Browser (React 18 + Vite) ]
                    │
                    ▼ HTTP / REST (JSON)
       [ FastAPI Application Server ]
  ┌─────────────────┼─────────────────────────┐
  ▼                 ▼                         ▼
[ Farm Health ]  [ ML Inference ]     [ External APIs ]
- Deterministic  - MobileNetV2        - Open-Meteo
  Risk Engine      (PyTorch)          - Agmarknet / APMC
- 6-Factor       - Leaf Quality Filter- Gemini Advisory
  Calculator
  │
  ▼
[ SQLite Database (SQLAlchemy ORM) ]
- Users & Farm Profiles
- Standing Crops (CurrentCrop)
- Soil Analysis History
- Active Weather & Disease Alerts
```

---

## 6. Farm Health & Risk Calculation Engine

The distress score ($0\text{--}100$) is calculated **deterministically** on the backend using application and sensor data:

$$\text{Distress Score} = \text{Weather (0--25)} + \text{Disease (0--20)} + \text{Market (0--20)} + \text{Crop/Yield (0--20)} + \text{Soil (0--10)} + \text{Context (0--5)}$$

### Risk Weightings:
- **Weather Risk (0–25)**: Evaluates 48-hour rainfall accumulation, extreme temperatures, and lodging wind speeds.
- **Disease Risk (0–20)**: Checks active disease alerts, standing crop status, and high humidity/warm temperature fungal predisposition.
- **Market Risk (0–20)**: Monitors APMC mandi 30-day price trajectories and flags sharp market crashes ($\le -12\%$).
- **Crop/Yield Risk (0–20)**: Evaluates standing crop maturity, harvest timing exposure, and irrigation intervals.
- **Soil Risk (0–10)**: Analyzes NPK balance, organic carbon rating, and soil pH extremes.
- **Context Risk (0–5)**: Flags unresolved critical alerts and farmer notification backlogs.

---

## 7. How to Run Locally

### Prerequisites
- Python 3.10+ (Python 3.11/3.12/3.14 compatible)
- Node.js 18+ and npm

### 1. Quick Start (Windows)
Double-click `start.bat` in the repository root to launch both backend and frontend servers automatically.

### 2. Manual Setup

**Terminal 1 — Backend:**
```bash
cd backend
# Create virtual environment (if not created)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run initial database setup (creates SQLite DB & tables)
python init_database.py

# Start FastAPI server
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

The application will be available at:
- **Frontend App**: `http://localhost:5173`
- **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`

---

## 8. Environment Variables

Create a `.env` file in the project root (see `.env.example`):

| Variable | Description | Default / Mode |
|---|---|---|
| `DATABASE_URL` | SQLite database connection string | `sqlite:///./crop_advisory.db` |
| `GEMINI_API_KEY` | Google Gemini API key for contextual advisories | Optional (graceful fallback) |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key (optional) | Optional (Open-Meteo fallback active) |
| `SENDGRID_API_KEY` | SendGrid key for email notifications | Optional (Mock mode in dev) |
| `TWILIO_ACCOUNT_SID` | Twilio SID for SMS OTP | Optional (Mock mode in dev) |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | Optional (Mock mode in dev) |
| `TWILIO_PHONE_NUMBER` | Twilio Registered Phone Number | Optional (Mock mode in dev) |
| `SECRET_KEY` | JWT signing secret key | `your-secret-key` |

> **Note**: For local hackathon evaluation, the prototype functions out-of-the-box in **Mock/Dev Mode** without requiring paid third-party SMS or Email credentials.

---

## 9. Recommended Demo Sequence

1. **Login Flow**:
   - Navigate to `http://localhost:5173/login`.
   - Enter registered farmer identifier: `ramesh@example.com` (or click "Register" to create a new farmer profile).
   - Click "Send OTP" $\to$ in mock/dev mode, OTP is displayed on screen $\to$ verify and enter.
2. **Dashboard Overview**:
   - Point out **Farmer & Farm Profile Header** (Name: Ramesh Kumar, Land: 4.5 Acres, Soil: Balanced, Active Crop: 🌱 Chilli).
   - Walk through the **Farm Health Centerpiece**: Score (`34 / 100`), `MODERATE RISK` badge, and `Risk increasing ↑` trend indicator.
   - Explain the **⚠️ Attention (Risk Factors)** section (e.g. Market price softness in local APMC yard, harvest timing proximity).
   - Show the **✓ Recommended Actions** (e.g. staggered selling, pre-harvest drainage preparation).
3. **Live Diagnostic Pulses**:
   - Review the **Live Weather Pulse** (Temp, Humidity, Wind).
   - Check **Local APMC Mandi Rates** (Chilli, Cotton, Rice rates with directional percentage changes).
   - Inspect **Plant Pathology Pulse** (Monitored status and 38-disease support).
4. **Interactive Feature Modules**:
   - **Disease Detection**: Click "Scan Crop Leaf with AI", upload a crop leaf image, view instant MobileNetV2 diagnosis and treatment advisory.
   - **Soil Analysis**: Input NPK values ($180, 22, 190, \text{pH } 6.8$), receive fertilizer recommendations and soil health classification.
   - **Crop Recommendation**: Select soil type and season to view ranked crop recommendations.
   - **APMC Market Prices**: Search commodity rates across Andhra Pradesh mandis.

---

## 10. Known Limitations

- **Mandi Price Latency**: Government mandi price updates depend on Agmarknet publishing frequency; cached seasonal trends are used as fallback during portal downtime.
- **Disease Dataset Bounds**: MobileNetV2 model supports 38 specific crop-disease classes across 14 species (PlantVillage dataset); non-leaf or out-of-domain images are safely flagged by the quality filter.
- **SMS / Email Gateways**: Real SMS delivery requires active Twilio credentials; dev mock mode provides full on-screen demonstration capability.
- **Microclimate Density**: Weather metrics reflect regional weather stations (Open-Meteo geocoded coordinates) rather than on-field IoT sensors.
