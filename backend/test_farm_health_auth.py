from fastapi.testclient import TestClient
from app import app
from database import SessionLocal
from models.user import User

client = TestClient(app)
db = SessionLocal()

# Ensure two distinct test users exist: User 1 and User 2
user1 = db.query(User).filter(User.id == 1).first()
if not user1:
    user1 = User(
        id=1,
        name="Ramesh Kumar (User A)",
        email="ramesh.auth1@example.com",
        phone="+919876543201",
        location="Guntur, Andhra Pradesh",
        language="en"
    )
    db.add(user1)
    db.commit()

user2 = db.query(User).filter(User.id == 2).first()
if not user2:
    user2 = User(
        id=2,
        name="Suresh Patel (User B)",
        email="suresh.auth2@example.com",
        phone="+919876543202",
        location="Kurnool, Andhra Pradesh",
        language="te"
    )
    db.add(user2)
    db.commit()

db.close()

print("=" * 60)
print("TESTING FARM HEALTH AUTHORIZATION & CROSS-USER ACCESS CONTROL")
print("=" * 60)

# Test 1: User A (authenticated as User 1) requests own Farm Health
res_own = client.get("/api/farm-health/risk?user_id=1&location=Guntur", headers={"X-User-ID": "1"})
print(f"Test 1 [User A requests User A data]: Status {res_own.status_code}")
assert res_own.status_code == 200, f"Expected 200, got {res_own.status_code}: {res_own.text}"
assert "score" in res_own.json()

# Test 2: User A (authenticated as User 1) attempts to request User B's (User 2) data -> MUST BE REJECTED
res_cross = client.get("/api/farm-health/risk?user_id=2&location=Kurnool", headers={"X-User-ID": "1"})
print(f"Test 2 [User A attempts to access User B data]: Status {res_cross.status_code}")
assert res_cross.status_code == 403, f"Expected 403 Forbidden, got {res_cross.status_code}: {res_cross.text}"
print(f"  -> Rejection message: {res_cross.json().get('detail')}")

# Test 3: User A (authenticated as User 1) with POST request attempts to access User B data -> MUST BE REJECTED
res_post_cross = client.post("/api/farm-health/risk", json={"user_id": 2, "location": "Kurnool"}, headers={"X-User-ID": "1"})
print(f"Test 3 [User A POST requests User B data]: Status {res_post_cross.status_code}")
assert res_post_cross.status_code == 403, f"Expected 403 Forbidden, got {res_post_cross.status_code}"

# Test 4: Unauthenticated request attempting to specify private user_id -> MUST BE REJECTED
res_unauth = client.get("/api/farm-health/risk?user_id=2&location=Kurnool")
print(f"Test 4 [Unauthenticated request for private user data]: Status {res_unauth.status_code}")
assert res_unauth.status_code == 401, f"Expected 401 Unauthorized, got {res_unauth.status_code}"

# Test 5: Unauthenticated generic location request -> Allowed
res_anon = client.get("/api/farm-health/risk?location=Vijayawada")
print(f"Test 5 [Anonymous location risk request]: Status {res_anon.status_code}")
assert res_anon.status_code == 200, f"Expected 200, got {res_anon.status_code}"

print("=" * 60)
print("ALL AUTHORIZATION TESTS PASSED: Cross-user access is strictly prevented!")
print("=" * 60)
