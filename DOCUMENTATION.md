# 🌾 Smart Crop Advisory System — Project Documentation

> **AI-powered agricultural decision support system for Indian farmers**
> Version: 1.0.0 | Built for: SIH Evaluation

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [How It Works — System Flow](#4-how-it-works--system-flow)
5. [Features & Functionalities](#5-features--functionalities)
6. [AI & ML Models](#6-ai--ml-models)
7. [API Reference](#7-api-reference)
8. [Database & Models](#8-database--models)
9. [Authentication System](#9-authentication-system)
10. [Frontend Pages](#10-frontend-pages)
11. [Multi-Language Support](#11-multi-language-support)
12. [External APIs Used](#12-external-apis-used)
13. [Environment Variables](#13-environment-variables)
14. [How to Run](#14-how-to-run)

---

## 1. Project Overview

The **Smart Crop Advisory System** is an intelligent, AI-powered web platform designed to help Indian farmers make data-driven agricultural decisions. The system combines:

- **Machine Learning** for plant disease detection and soil type classification
- **Google Gemini 2.5 Flash** (LLM) for generating structured, farmer-friendly advisories
- **Live weather data** from Open-Meteo (free, no API key required)
- **Market price intelligence** for crop price trends across Indian states
- **Climate alerts** to warn farmers about extreme weather events

The platform is designed specifically for Indian agriculture — it supports **7 regional languages**, covers all major **Indian states**, and includes crop data relevant to Indian farming seasons (Kharif, Rabi, Summer).

---

## 2. Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | **FastAPI** 0.115.0 |
| Server | **Uvicorn** (ASGI) |
| Database | **SQLite** (via SQLAlchemy 2.0) |
| AI/LLM | **Google Gemini 2.5 Flash** (google-genai SDK) |
| ML Framework | **PyTorch** + **TorchVision** |
| Image Processing | **Pillow** |
| Numeric Computing | **NumPy** |
| Config | **Pydantic-Settings** + **python-dotenv** |
| HTTP Client | **Requests** |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | **React** (with Vite) |
| Build Tool | **Vite** |
| Routing | **React Router** |
| Styling | Vanilla CSS (custom design system) |
| i18n | Custom i18n implementation |
| API Calls | Fetch API |

---

## 3. Project Structure

```
SIH evaluation222 - pavani/
│
├── .env                        # Environment variables (API keys, DB URL)
├── .env.example                # Template for environment setup
├── start.ps1                   # One-click PowerShell startup script
├── start.bat                   # Batch file launcher
├── start-debug.bat             # Debug mode launcher
├── stop.bat                    # Stop all servers
├── diagnose.bat                # Diagnostic checks
│
├── backend/                    # Python FastAPI backend
│   ├── app.py                  # Main FastAPI application entry point
│   ├── config.py               # Settings/configuration (Pydantic)
│   ├── database.py             # SQLAlchemy DB setup + session
│   ├── init_database.py        # DB initialization script
│   ├── requirements.txt        # Python dependencies
│   │
│   ├── routes/                 # API Route handlers
│   │   ├── auth.py             # User registration & OTP login
│   │   ├── crop_recommendation.py  # Crop recommendation endpoint
│   │   ├── disease_detection.py    # Plant disease detection endpoint
│   │   ├── market_prices.py        # Market price data endpoint
│   │   ├── soil_analysis.py        # Soil nutrient analysis endpoint
│   │   └── weather.py             # Weather & climate alerts endpoint
│   │
│   ├── services/               # Business logic layer
│   │   ├── gemini_service.py       # Google Gemini AI advisory generator
│   │   ├── crop_recommendation.py  # Multi-factor crop recommendation engine
│   │   ├── disease_detection.py    # MobileNetV2 disease ML inference
│   │   ├── soil_detection.py       # Soil type image classification
│   │   ├── weather_service.py      # Open-Meteo weather integration
│   │   ├── market_price_service.py # Crop price trends & state data
│   │   ├── climate_alert.py        # Extreme weather alert detection
│   │   ├── email_service.py        # SendGrid email integration
│   │   ├── otp_service.py          # OTP generation & verification
│   │   └── context_service.py      # User context management
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py             # User table
│   │   └── soil_analysis_history.py  # Soil analysis history table
│   │
│   ├── ml_models/              # ML model weights storage
│   │   └── plant_disease/
│   │       ├── mobilenetv2_plant.pth   # Trained MobileNetV2 weights
│   │       └── class_names.json        # 38 disease class labels
│   │
│   ├── data/
│   │   └── crops.json          # Crops database (nutrients, seasons, states)
│   │
│   ├── locales/                # Backend translation files
│   └── templates/              # Email HTML templates
│
└── frontend/                   # React + Vite frontend
    ├── index.html              # Entry HTML
    ├── vite.config.js          # Vite dev server config
    ├── package.json            # Node dependencies
    │
    └── src/
        ├── main.jsx            # React app entry
        ├── App.jsx             # Root component with routing
        │
        ├── pages/              # Page-level components
        │   ├── Landing.jsx         # Home / landing page
        │   ├── Login.jsx           # OTP login page
        │   ├── Register.jsx        # User registration page
        │   ├── Dashboard.jsx       # User dashboard
        │   ├── DiseaseDetection.jsx    # Upload image → detect disease
        │   ├── SoilAnalysis.jsx        # Enter soil nutrients → analysis
        │   ├── SoilTypeDetection.jsx   # Upload image → detect soil type
        │   ├── CropRecommendation.jsx  # Get crop recommendations
        │   ├── Weather.jsx             # Live weather + climate alerts
        │   ├── MarketPrices.jsx        # Crop market prices by state
        │   ├── AlertDetail.jsx         # Detailed climate alert view
        │   └── About.jsx               # About the platform
        │
        ├── components/         # Reusable UI components
        ├── styles/             # Global CSS stylesheets
        ├── i18n/               # i18n configuration
        └── locales/            # Frontend translation JSON files
```

---

## 4. How It Works — System Flow

```
User (Browser)
    │
    ├──► React Frontend (http://localhost:5173)
    │         │
    │         ▼
    │    User selects feature (e.g., Disease Detection)
    │         │
    │         ▼
    │    Sends API request to Backend
    │
    ▼
FastAPI Backend (http://localhost:8000)
    │
    ├──► Route Handler (e.g., /api/disease/detect)
    │         │
    │         ▼
    │    Service Layer:
    │         ├── ML Model inference (MobileNetV2 for disease)
    │         ├── External API calls (Weather, Market Data)
    │         └── Gemini AI advisory generation
    │
    ├──► SQLite Database (crop_advisory.db)
    │         └── User data, soil analysis history
    │
    └──► Returns structured JSON response to Frontend
```

**Key Design Principle**: Gemini AI is used **only to explain**, not to decide. All decisions (crop suitability, disease detection, soil classification) are made by dedicated algorithms/ML models. Gemini then generates a farmer-friendly explanation of those results.

---

## 5. Features & Functionalities

### 🌿 Feature 1: Plant Disease Detection
- **What it does**: Identifies plant diseases from a leaf photo
- **How it works**:
  1. User uploads a photo of a crop leaf
  2. MobileNetV2 ML model classifies it into one of 38 classes (disease types)
  3. Returns: crop name, disease name, confidence score, healthy/unhealthy flag
  4. Gemini AI generates a structured advisory with treatment steps
- **Supported crops**: Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato (healthy + diseases)
- **Output sections**: Summary, Analysis, Treatment, Prevention, Key Actions

---

### 🌱 Feature 2: Soil Analysis (Nutrient-Based)
- **What it does**: Analyzes soil nutrient parameters and recommends fertilizers
- **How it works**:
  1. User enters soil nutrient values: N, P, K (nitrogen, phosphorus, potassium), pH, organic matter
  2. Backend evaluates soil health score
  3. Recommends appropriate fertilizers based on deficiencies
  4. Gemini AI explains the results with fertilizer guidance
- **Output sections**: Summary, Nutrient Analysis, Fertilizer Guidance, Precautions, Key Actions
- **Saves history**: Analysis is stored per user in the database

---

### 📷 Feature 3: Soil Type Detection (Image-Based)
- **What it does**: Identifies soil type from an uploaded soil photo
- **How it works**:
  1. User uploads a photo of their soil
  2. Image classification model analyses color, texture
  3. Returns: soil type, confidence score, and soil characteristics
  4. Gemini AI gives crop suitability explanation
- **Detectable Soil Types**:

| Soil Type | Best Crops |
|-----------|-----------|
| Clay | Rice, Wheat, Pulses |
| Sandy | Millet, Groundnut, Watermelon |
| Loamy | Vegetables, Fruits, Grains |
| Silty | Vegetables, Grass crops |
| Black Soil | Cotton, Sugarcane, Jowar |
| Red Soil | Groundnut, Millets, Tobacco |
| Alluvial | Rice, Wheat, Sugarcane, Cotton |
| Peaty | Specialty crops |
| Chalky | Adapted crops |
| Laterite | Root crops |

---

### 🌾 Feature 4: Crop Recommendation Engine
- **What it does**: Recommends the best crops based on multi-factor analysis
- **How it works** (9-step pipeline):
  1. Takes user inputs: soil type, location (state), season
  2. Loads soil context from user's latest soil analysis (from DB) or manual input
  3. Fetches **live weather forecast** (temperature, rainfall) for location
  4. Scores each crop from crops database by: soil match (+3), state match (+2), season match (+2), temperature range (+1)
  5. Filters top 10 scoring candidates
  6. Fetches **market price data** for all candidates
  7. Excludes crops with market trend **down > 15%** (severely unfavorable)
  8. Checks for **active climate alerts** for the region
  9. Sends all structured data to Gemini AI → generates final explanation
- **Seasons supported**: Kharif, Rabi, Summer (auto-detected from current date)
- **Output**: Ranked crop list with market trends + AI advisory

---

### 🌦️ Feature 5: Live Weather & Climate Alerts
- **What it does**: Shows real-time weather and warns farmers about extreme events
- **How it works**:
  1. User selects their state/city
  2. Backend fetches live data from Open-Meteo API (free, no key needed)
  3. Analyzes conditions for climate alerts (extreme heat, heavy rain, strong winds, drought)
  4. Returns current weather (temp, humidity, wind, description) + 5-day forecast
  5. Gemini AI generates alert advisories for any detected events
- **Alert Types Detected**: Extreme Heat, Heavy Rain/Flood risk, Strong Winds, Drought, Thunderstorm
- **Coverage**: All Indian states and major cities
- **API**: Open-Meteo (geocoding + forecast, completely free)

---

### 📈 Feature 6: Market Price Intelligence
- **What it does**: Shows current crop prices and trends by Indian state
- **How it works**:
  1. User selects crop and state/location
  2. Backend loads market price data for that state and crop
  3. Calculates price trend (up/down/stable) and percentage change
  4. Gemini AI generates market timing advisory (when to sell/hold)
- **Coverage**: All major Indian states
- **Output sections**: Summary, Price Insight, Action Suggestions, Key Actions

---

### 🔐 Feature 7: User Authentication (OTP-Based)
- **What it does**: Passwordless login via OTP (email or SMS)
- **Registration fields**: Name, Email, Phone, Location (state), Preferred Language
- **Login methods**:
  - Email OTP (via SendGrid email service)
  - SMS OTP (via Twilio)
  - In development mode: OTP is shown directly in API response
- **Session**: User ID stored in browser localStorage (no JWT complexity)
- **User settings**: Language and location can be updated anytime

---

## 6. AI & ML Models

### Model 1: Google Gemini 2.5 Flash (LLM)
| Property | Value |
|----------|-------|
| **Model Name** | `gemini-2.5-flash` |
| **SDK** | `google-genai` (>=1.0.0) |
| **Purpose** | Generate all farmer-facing advisories |
| **API Key** | Required (set `GEMINI_API_KEY` in `.env`) |
| **Rate Limiting** | Min 2 seconds between requests |
| **Caching** | MD5-keyed response cache (60s TTL) |
| **Temperature** | 0.5–0.7 (varies by advisory type) |

**Advisory types generated by Gemini:**
- Disease advisory (treatment, prevention)
- Climate alert advisory (risk explanation, protective actions)
- Crop recommendation explanation (why each crop is suitable)
- Soil analysis explanation (nutrient assessment, fertilizer guidance)
- Soil type explanation (characteristics, best crops, improvement tips)
- Market price advisory (trend insight, timing recommendations)

**Output format**: Structured Markdown with `##` headings and bullet points — directly rendered in the UI.

**Language support**: Full advisories can be generated in English, Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati using Gemini's multilingual capability.

---

### Model 2: MobileNetV2 — Plant Disease Detection
| Property | Value |
|----------|-------|
| **Architecture** | MobileNetV2 (torchvision) |
| **Source** | `Daksh159/plant-disease-mobilenetv2` |
| **Weights file** | `backend/ml_models/plant_disease/mobilenetv2_plant.pth` |
| **Classes** | 38 (plant + disease combinations) |
| **Input** | RGB image, resized to 224×224 |
| **Preprocessing** | ImageNet normalization (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]) |
| **Output** | Class probabilities via Softmax |
| **Classifier head** | `Dropout(0.2)` → `Linear(1280 → 38)` |
| **Inference mode** | `torch.no_grad()` (CPU) |
| **Fallback** | Mock random prediction if model file missing |

**38 Disease Classes** (format: `Crop___Disease`):
- Apple (healthy, Apple scab, Black rot, Cedar apple rust)
- Blueberry (healthy)
- Cherry (healthy, Powdery mildew)
- Corn (healthy, Cercospora leaf spot, Common rust, Northern leaf blight)
- Grape (healthy, Black rot, Esca, Leaf blight)
- Orange (Haunglongbing/Citrus greening)
- Peach (healthy, Bacterial spot)
- Pepper (healthy, Bacterial spot)
- Potato (healthy, Early blight, Late blight)
- Raspberry (healthy)
- Soybean (healthy)
- Squash (Powdery mildew)
- Strawberry (healthy, Leaf scorch)
- Tomato (healthy + 9 disease types)

---

### Model 3: Soil Type Detection (Image-Based)
| Property | Value |
|----------|-------|
| **Architecture** | Custom image classifier |
| **Classes** | 10 soil types |
| **Input** | RGB image, resized to 224×224 |
| **Status** | Mock predictions (production model slot ready) |
| **Analysis method** | Color and texture analysis |
| **Fallback** | Random soil type with realistic confidence (80–98%) |

---

## 7. API Reference

**Base URL**: `http://localhost:8000`
**Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)

### Authentication Endpoints (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login/request-otp` | Send OTP (email or SMS) |
| POST | `/api/auth/login/verify-otp` | Verify OTP and login |
| GET | `/api/auth/user/{user_id}` | Get user details |
| PUT | `/api/auth/user/{user_id}` | Update user settings |

### Disease Detection Endpoints (`/api/disease`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/disease/detect` | Upload image → detect disease + Gemini advisory |

### Soil Analysis Endpoints (`/api/soil`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/soil/analyze` | Analyze soil nutrients (N, P, K, pH, organic matter) |
| GET | `/api/soil/history/{user_id}` | Get soil analysis history |
| POST | `/api/soil/detect-type` | Upload image → detect soil type |

### Crop Recommendation Endpoints (`/api/crops`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/crops/recommend` | Get multi-factor crop recommendations |
| GET | `/api/crops/all` | Get all crops in database |
| GET | `/api/crops/search?q=` | Search crops by name |

### Weather Endpoints (`/api/weather`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/weather/current?location=` | Get current weather |
| GET | `/api/weather/forecast?location=` | Get 5-day forecast |
| GET | `/api/weather/alerts?location=` | Get climate alerts |

### Market Price Endpoints (`/api/market`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/market/prices?crop=&location=` | Get crop price + trend |
| GET | `/api/market/states` | Get all supported Indian states |
| GET | `/api/market/crops` | Get all crops with market data |

### System Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |

---

## 8. Database & Models

**Database**: SQLite (`backend/crop_advisory.db`)
**ORM**: SQLAlchemy 2.0

### Table: `users`
| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Auto-increment primary key |
| `name` | String | Full name |
| `email` | String (unique) | Email address |
| `phone` | String (unique) | Phone number |
| `location` | String | State/region |
| `language` | String | Preferred language code (en, hi, te, etc.) |
| `last_login` | DateTime | Last login timestamp |

### Table: `soil_analysis_history`
| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Auto-increment primary key |
| `user_id` | Integer (FK) | Reference to users table |
| `soil_type` | String | Detected/entered soil type |
| `nitrogen` | Float | N value (kg/ha) |
| `phosphorus` | Float | P value (kg/ha) |
| `potassium` | Float | K value (kg/ha) |
| `ph` | Float | Soil pH (0–14) |
| `organic_matter` | Float | Organic matter percentage |
| `soil_health` | String | Health rating (Poor/Moderate/Good/Excellent) |
| `analysis_date` | DateTime | Timestamp of analysis |

---

## 9. Authentication System

The platform uses **passwordless OTP authentication** — no passwords stored.

### Flow:
```
1. Register → User fills name, email, phone, location, language
2. Login → Enter email OR phone  →  System sends 6-digit OTP
3. Enter OTP → Verified → User session starts (user ID in localStorage)
4. Dev Mode → OTP is returned in API response (no email/SMS needed)
```

### OTP Details:
- **Length**: 6 digits
- **Expiry**: 10 minutes
- **Email OTP**: via SendGrid (requires `SENDGRID_API_KEY`)
- **SMS OTP**: via Twilio (requires Twilio credentials)
- **Dev mode**: When no email/SMS service is configured, OTP is included in the API response for easy testing

---

## 10. Frontend Pages

| Page | Route | Description |
|------|-------|-------------|
| **Landing** | `/` | Hero page with feature overview and CTA |
| **Login** | `/login` | OTP login form |
| **Register** | `/register` | New user registration |
| **Dashboard** | `/dashboard` | User home with all feature cards |
| **Disease Detection** | `/disease-detection` | Upload crop photo → get disease analysis |
| **Soil Analysis** | `/soil-analysis` | Enter NPK/pH → get soil health report |
| **Soil Type Detection** | `/soil-type-detection` | Upload soil photo → detect soil type |
| **Crop Recommendation** | `/crop-recommendation` | Select soil + location → get crop advice |
| **Weather** | `/weather` | Live weather + 5-day forecast + alerts |
| **Market Prices** | `/market-prices` | State-wise crop market prices + trends |
| **Alert Detail** | `/alerts/:id` | Detailed view of a specific climate alert |
| **About** | `/about` | Platform information and team details |

---

## 11. Multi-Language Support

The platform supports **7 languages** for all AI-generated advisories:

| Code | Language | Script |
|------|----------|--------|
| `en` | English | Latin |
| `hi` | Hindi | हिन्दी |
| `ta` | Tamil | தமிழ் |
| `te` | Telugu | తెలుగు |
| `bn` | Bengali | বাংলা |
| `mr` | Marathi | मराठी |
| `gu` | Gujarati | ગુજરાતી |

- Language is set at registration and can be changed in user settings
- All Gemini AI advisories are generated in the user's preferred language
- The language instruction is appended to every Gemini prompt with native script examples for stronger enforcement
- Frontend UI also has i18n support via `/src/locales/` JSON files

---

## 12. External APIs Used

| API | Purpose | Cost | Key Required |
|-----|---------|------|-------------|
| **Google Gemini 2.5 Flash** | AI advisory generation | Free tier (quota limited) | Yes — `GEMINI_API_KEY` |
| **Open-Meteo** | Live weather + 5-day forecast + geocoding | Completely Free | No |
| **SendGrid** | Email OTP delivery | Free tier (100 emails/day) | Optional |
| **Twilio** | SMS OTP delivery | Paid (trial available) | Optional |
| **data.gov.in** | Live market prices (future) | Free with registration | Optional |

### Open-Meteo Details:
- Geocoding: `https://geocoding-api.open-meteo.com/v1/search`
- Weather: `https://api.open-meteo.com/v1/forecast`
- Fields fetched: `temperature_2m`, `relativehumidity_2m`, `precipitation`, `windspeed`, daily summaries
- Mapped to WMO weather codes for human-readable descriptions

---

## 13. Environment Variables

File: `.env` (in project root)

```env
# Database
DATABASE_URL=sqlite:///./crop_advisory.db

# AI (REQUIRED)
GEMINI_API_KEY=your_gemini_api_key_here

# Weather (Optional - fallback to Open-Meteo if missing)
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Email OTP (Optional)
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=noreply@cropadvisory.com

# SMS OTP (Optional)
TWILIO_ACCOUNT_SID=your_twilio_sid_here
TWILIO_AUTH_TOKEN=your_twilio_token_here
TWILIO_PHONE_NUMBER=+1234567890

# Market Data (Optional)
DATA_GOV_IN_API_KEY=

# JWT / Security
SECRET_KEY=change_this_to_secure_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# URLs
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

**Minimum required key**: `GEMINI_API_KEY` — without it, AI advisories will not generate.

---

## 14. How to Run

### Quick Start (Recommended)
```powershell
# Run the PowerShell startup script (auto-installs dependencies)
powershell -ExecutionPolicy Bypass -File start.ps1
```

This script automatically:
1. Creates Python virtual environment (if missing)
2. Installs Python dependencies (pip install -r requirements.txt)
3. Initializes the SQLite database
4. Starts the backend server in a new window (`python app.py` on port 8000)
5. Installs Node dependencies (if missing)
6. Starts the frontend dev server in a new window (`npm run dev` on port 5173)
7. Opens the app in your browser

### Manual Start (if needed)

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pydantic-settings email-validator
python init_database.py
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Access URLs
| Service | URL |
|---------|-----|
| Frontend App | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |

### Stop Servers
```bash
# Run stop.bat, OR close the two PowerShell windows that opened
stop.bat
```

---

## 📌 Key Design Decisions

1. **Gemini explains, algorithms decide** — ML models and rule engines make the actual recommendations. Gemini only translates data into human-readable advisories.

2. **Free-first architecture** — Core weather data uses Open-Meteo (no API key). The only paid/key-required service is Gemini.

3. **Rate limiting & caching** — Gemini responses are cached for 60 seconds with MD5 keys. Minimum 2-second gap between API calls to protect the free tier quota.

4. **Offline fallback** — If any ML model weights are missing, the system uses randomized mock predictions so the UI remains functional for demos.

5. **India-first** — The crops database, soil types, state/city lists, seasons, and language support are all tailored for Indian agriculture.

6. **OTP-only auth** — No password storage reduces security risk. Works in demo mode without email/SMS services configured.

---

*Documentation generated: March 2026 | Smart Crop Advisory System v1.0.0*
