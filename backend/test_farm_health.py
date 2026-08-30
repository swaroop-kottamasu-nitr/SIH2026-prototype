import json
from datetime import datetime, timedelta, date
from fastapi.testclient import TestClient
from app import app
from database import SessionLocal
from models.user import User
from models.soil_analysis_history import SoilAnalysisHistory
from models.alert import Alert, AlertSeverity
from models.current_crop import CurrentCrop

client = TestClient(app)
db = SessionLocal()

# Ensure a test user exists
user = db.query(User).filter(User.id == 1).first()
if not user:
    user = User(
        name='Ramesh Kumar',
        email='ramesh@example.com',
        phone='+919876543210',
        location='Guntur, Andhra Pradesh',
        language='te',
        farm_size=4.5,
        farming_experience=12,
        preferred_crops=['Chilli', 'Cotton', 'Rice']
    )
    db.add(user)
    db.commit()
    db.refresh(user)

# Add sample soil test if none
soil = db.query(SoilAnalysisHistory).filter(SoilAnalysisHistory.user_id == 1).first()
if not soil:
    soil = SoilAnalysisHistory(
        user_id=1,
        soil_type='Black Soil',
        nitrogen=220.0,
        phosphorus=18.5,
        potassium=210.0,
        ph=7.2,
        soil_health='Good',
        location='Guntur, Andhra Pradesh'
    )
    db.add(soil)
    db.commit()

# Add sample standing crop if none
crop = db.query(CurrentCrop).filter(CurrentCrop.user_id == 1).first()
if not crop:
    crop = CurrentCrop(
        user_id=1,
        crop_name='Chilli',
        planting_date=date.today() - timedelta(days=90),
        expected_harvest_date=date.today() + timedelta(days=10),
        field_size=2.0,
        health_status='healthy'
    )
    db.add(crop)
    db.commit()

db.close()

# 1. Test GET farm risk for user
r1 = client.get('/api/farm-health/risk?user_id=1&location=Guntur')
print('=== 1. USER FARM HEALTH RISK (GET) ===')
print('Status:', r1.status_code)
d1 = r1.json()
print('Score:', d1['score'], '/ 100 -- Level:', d1['risk_level'])
print('Factors:')
for f in d1['factors']:
    print(f"  • {f['name']}: {f['score']}/{f['max_score']} ({f['level']}) -> {f['reason']}")
print('Recommendations:')
for rec in d1['recommendations']:
    print(f"  - {rec}")

assert r1.status_code == 200
assert 0 <= d1['score'] <= 100
assert d1['risk_level'] in ['LOW', 'MODERATE', 'HIGH', 'CRITICAL']
assert len(d1['factors']) == 6
assert 2 <= len(d1['recommendations']) <= 4

# 2. Test GET farm risk for generic location (guest user)
r2 = client.get('/api/farm-health/risk?location=Vijayawada')
print('\n=== 2. GUEST FARM HEALTH RISK (GET) ===')
print('Status:', r2.status_code)
d2 = r2.json()
print('Score:', d2['score'], '/ 100 -- Level:', d2['risk_level'])
assert r2.status_code == 200

# 3. Test POST farm risk
r3 = client.post('/api/farm-health/risk', json={'user_id': 1, 'location': 'Kurnool'})
print('\n=== 3. POST FARM HEALTH RISK ===')
print('Status:', r3.status_code)
d3 = r3.json()
print('Score:', d3['score'], '/ 100 -- Level:', d3['risk_level'])
assert r3.status_code == 200

print('\nALL FARM HEALTH VERIFICATIONS COMPLETED SUCCESSFULLY!')
