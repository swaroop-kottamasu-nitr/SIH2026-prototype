"""
Database Initialization Script for AgriDarshak

This script initializes all database tables including new models:
- SoilAnalysisHistory
- CropHistory  
- CurrentCrop
- Updated User model

Run this after installing backend dependencies.
"""

import sys
import os

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import Base, engine, init_db
    from models.user import User
    from models.alert import Alert
    from models.market_price import MarketPrice
    from models.soil_analysis_history import SoilAnalysisHistory
    from models.crop_history import CropHistory
    from models.current_crop import CurrentCrop
    
    print("=" * 60)
    print("AgriDarshak - Database Initialization")
    print("=" * 60)
    print()
    
    print("[INIT] Importing models...")
    print("  * User")
    print("  * Alert")
    print("  * MarketPrice")
    print("  * SoilAnalysisHistory")
    print("  * CropHistory")
    print("  * CurrentCrop")
    print()
    
    print("[INIT] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("  * All tables created successfully")
    print()
    
    # Check if default test user exists, seed if missing
    from database import get_db
    from models.user import User
    db = next(get_db())
    test_user = db.query(User).filter(User.id == 1).first()
    if not test_user:
        print("[INIT] Seeding initial test farmer profile...")
        new_user = User(
            id=1,
            name="Ramesh Chandra Sahoo",
            email="ramesh.sahoo@agridarshak.in",
            phone="9876543210",
            location="Rourkela, Odisha",
            language="or",
            farm_size=4.5,
            farming_experience=12,
            preferred_crops=["Chilli", "Paddy", "Brinjal"]
        )
        db.add(new_user)
        db.commit()
        print("  * Seeded farmer: Ramesh Chandra Sahoo (ID: 1, Location: Rourkela, Odisha)")
    db.close()

    print("=" * 60)
    print("[OK] Database initialization completed successfully!")
    print("=" * 60)
    print()
    
except ImportError as e:
    print()
    print("[ERROR] Missing dependencies:")
    print(f"   {str(e)}")
    print()
    sys.exit(1)
    
except Exception as e:
    print()
    print(f"[ERROR] {str(e)}")
    print()
    sys.exit(1)
