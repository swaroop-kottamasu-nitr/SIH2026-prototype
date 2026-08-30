import io
from PIL import Image
from fastapi.testclient import TestClient
from app import app
from database import SessionLocal
from models.user import User

client = TestClient(app)

print("=" * 60)
print("SIH 2026 PROTOTYPE COMPLETE FLOW VERIFICATION TEST")
print("=" * 60)

# Step 1: LOGIN (Request OTP & Verify OTP)
db = SessionLocal()
user = db.query(User).filter(User.id == 1).first()
if not user:
    user = User(
        name="Ramesh Kumar",
        email="ramesh@example.com",
        phone="+919876543210",
        location="Guntur, Andhra Pradesh",
        language="en",
        farm_size=4.5,
        farming_experience=12,
        preferred_crops=["Chilli", "Cotton", "Rice"]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
db.close()

# Request OTP
res_otp_req = client.post("/api/auth/login/request-otp", json={"identifier": user.email, "method": "email"})
assert res_otp_req.status_code == 200, f"OTP request failed: {res_otp_req.text}"
otp_val = res_otp_req.json().get("otp")
print(f"✓ Step 1a: OTP Requested successfully (Mock/Dev OTP: {otp_val})")

# Verify OTP
res_otp_ver = client.post("/api/auth/login/verify-otp", json={"identifier": user.email, "otp": otp_val, "method": "email"})
assert res_otp_ver.status_code == 200, f"OTP verify failed: {res_otp_ver.text}"
logged_in_user = res_otp_ver.json()
print(f"✓ Step 1b: User Logged In -> {logged_in_user['name']} (ID: {logged_in_user['id']})")

# Step 2: FARMER DASHBOARD PROFILE
res_user = client.get(f"/api/auth/user/{logged_in_user['id']}")
assert res_user.status_code == 200
print(f"✓ Step 2: Farmer Profile Loaded -> Location: {res_user.json()['location']}")

# Step 3: FARM HEALTH SCORE & 4: RISK FACTORS & 5: RECOMMENDATIONS
res_health = client.get(
    f"/api/farm-health/risk?user_id={logged_in_user['id']}&location=Guntur",
    headers={"X-User-ID": str(logged_in_user['id'])}
)
assert res_health.status_code == 200, f"Farm health returned {res_health.status_code}: {res_health.text}"
h_data = res_health.json()
assert 0 <= h_data['score'] <= 100
assert h_data['risk_level'] in ['LOW', 'MODERATE', 'HIGH', 'CRITICAL']
assert len(h_data['factors']) == 6
assert 2 <= len(h_data['recommendations']) <= 4
print(f"✓ Step 3, 4, 5: Farm Health Score: {h_data['score']}/100 [{h_data['risk_level']} RISK]")
for f in h_data['factors']:
    print(f"    - {f['name']}: {f['score']}/{f['max_score']} -> {f['reason']}")
print(f"  Recommendations count: {len(h_data['recommendations'])}")

# Step 6: WEATHER CURRENT & FORECAST
res_w = client.post("/api/weather/current", json={"location": "Guntur, Andhra Pradesh"})
assert res_w.status_code == 200
print(f"✓ Step 6a: Live Weather -> Temp: {res_w.json()['main']['temp']}°C, Humidity: {res_w.json()['main']['humidity']}%")

res_fc = client.post("/api/weather/forecast", json={"location": "Guntur, Andhra Pradesh"}, params={"days": 5})
assert res_fc.status_code == 200
print(f"✓ Step 6b: 5-Day Forecast -> {len(res_fc.json().get('forecast', []))} intervals returned")

# Step 7: APMC MANDI MARKET PRICES
res_mandi = client.post("/api/market/season-prices", json={"location": "Guntur, Andhra Pradesh"})
assert res_mandi.status_code == 200
print(f"✓ Step 7: Mandi Season Prices -> {len(res_mandi.json().get('crops', []))} crops tracked")

# Step 8: SOIL NPK ANALYSIS & RECOMMENDATIONS
res_soil = client.post("/api/soil/analyze", json={
    "user_id": logged_in_user['id'],
    "nitrogen": 180.0,
    "phosphorus": 22.0,
    "potassium": 190.0,
    "ph": 6.8,
    "organic_matter": 1.2,
    "soil_type": "Black Soil",
    "location": "Guntur, Andhra Pradesh"
})
assert res_soil.status_code == 200
print(f"✓ Step 8: Soil Analysis -> Health Status: {res_soil.json()['soil_health']}")

# Step 9: CROP RECOMMENDATION ENGINE
res_crop = client.post("/api/crop/recommend", json={
    "user_id": logged_in_user['id'],
    "soil_type": "Black Soil",
    "location": "Andhra Pradesh",
    "season": "Kharif",
    "temperature": 29.0
})
assert res_crop.status_code == 200
crops_rec = res_crop.json().get('recommendations', [])
print(f"✓ Step 9: Crop Recommendations -> {len(crops_rec)} crops recommended: {[c['crop_name'] for c in crops_rec[:3]]}")

# Step 10: DISEASE DETECTION ON LEAF IMAGE
import numpy as np
np.random.seed(42)
img_array = np.random.randint(40, 180, (224, 224, 3), dtype=np.uint8)
img_array[:, :, 1] = np.clip(img_array[:, :, 1] + 50, 0, 255)  # Make it predominantly green
img = Image.fromarray(img_array)
buf = io.BytesIO()
img.save(buf, format='JPEG')
buf.seek(0)

res_disease = client.post(
    "/api/disease/detect",
    data={"user_id": logged_in_user['id'], "language": "en", "send_email": "false"},
    files={"image": ("test_leaf.jpg", buf, "image/jpeg")}
)
assert res_disease.status_code == 200, f"Disease detection returned {res_disease.status_code}: {res_disease.text}"
print(f"✓ Step 10: Leaf Pathology AI -> Detected: {res_disease.json()['disease_name']} ({res_disease.json()['crop_name']})")

print("=" * 60)
print("COMPLETE END-TO-END FLOW PASSED WITH 100% SUCCESS!")
print("=" * 60)
