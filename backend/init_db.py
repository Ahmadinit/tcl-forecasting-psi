from database import engine, SessionLocal
from models import Base, ProductModel, SystemConfig
from sqlalchemy import text
import datetime

def init_database():
    """Initialize database with default data"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if products already exist to avoid duplicates
        existing_products = db.query(ProductModel).first()
        if existing_products:
            print("Database already initialized")
            return
        
        # Insert default product models from the Excel sheet
        products = [
            # 2025 Products
            {"sku": "32S55", "name": "32S55", "shipping_mode": "CKD F", "status": "2025 Product", "safety_stock_days": 45},
            {"sku": "43S55", "name": "43S55", "shipping_mode": "CKD F", "status": "2025 Product", "safety_stock_days": 45},
            {"sku": "50S55", "name": "50S55", "shipping_mode": "CKD F", "status": "2025 Product", "safety_stock_days": 45},
            {"sku": "43U65", "name": "43U65", "shipping_mode": "CKD F", "status": "2025 Product", "safety_stock_days": 45},
            {"sku": "50U65", "name": "50U65", "shipping_mode": "CKD F", "status": "2025 Product", "safety_stock_days": 45},
            {"sku": "55U65", "name": "55U65", "shipping_mode": "CKD F", "status": "2025 Product", "safety_stock_days": 45},
            {"sku": "65U65", "name": "65U65", "shipping_mode": "CKD F", "status": "2025 Product", "safety_stock_days": 45},
            {"sku": "75U65", "name": "75U65", "shipping_mode": "CKD F", "status": "2025 Product", "safety_stock_days": 45},
            
            # 2026 New Products
            {"sku": "55U75A", "name": "55U75A", "shipping_mode": "CKD F", "status": "2026 New Product", "safety_stock_days": 60},
            {"sku": "65U75A", "name": "65U75A", "shipping_mode": "CKD F", "status": "2026 New Product", "safety_stock_days": 60},
            {"sku": "75U75A", "name": "75U75A", "shipping_mode": "CKD F", "status": "2026 New Product", "safety_stock_days": 60},
            {"sku": "85U75A", "name": "85U75A", "shipping_mode": "CKD F", "status": "2026 New Product", "remarks": "First batch complete machine", "safety_stock_days": 60},
            {"sku": "55U95A", "name": "55U95A", "shipping_mode": "CKD F", "status": "2026 New Product", "remarks": "First batch complete machine", "safety_stock_days": 60},
            {"sku": "65U95A", "name": "65U95A", "shipping_mode": "CKD F", "status": "2026 New Product", "remarks": "First batch complete machine", "safety_stock_days": 60},
            {"sku": "75U95A", "name": "75U95A", "shipping_mode": "CKD F", "status": "2026 New Product", "remarks": "First batch complete machine", "safety_stock_days": 60},
            {"sku": "85U95A", "name": "85U95A", "shipping_mode": "CKD F", "status": "2026 New Product", "remarks": "First batch complete machine", "safety_stock_days": 60},
            {"sku": "98U95A", "name": "98U95A", "shipping_mode": "CKD F", "status": "2026 New Product", "remarks": "First batch complete machine", "safety_stock_days": 60},
        ]
        
        for product_data in products:
            product = ProductModel(**product_data)
            db.add(product)
        
        # Insert system configuration
        configs = [
            {"config_key": "lead_time_shipping", "config_value": "45", "description": "Shipping time in days"},
            {"config_key": "lead_time_customs", "config_value": "10", "description": "Customs clearance time in days"},
            {"config_key": "lead_time_production", "config_value": "15", "description": "Production to warehouse time in days"},
            {"config_key": "total_lead_time", "config_value": "70", "description": "Total lead time in days"},
            {"config_key": "order_advance_time", "config_value": "28", "description": "Days before ETD to place order"},
            {"config_key": "forecast_weights", "config_value": "0.5,0.3,0.15,0.05", "description": "Weighted moving average weights"},
            {"config_key": "target_dos_new", "config_value": "50,60", "description": "Target DOS range for new branches"},
            {"config_key": "target_dos_established", "config_value": "0,45", "description": "Target DOS range for established branches"},
        ]
        
        for config_data in configs:
            config = SystemConfig(**config_data)
            db.add(config)
        
        db.commit()
        print("Database initialized successfully with default data")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()