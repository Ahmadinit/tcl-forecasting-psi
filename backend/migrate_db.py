"""
Database migration script to add new columns to existing database
Run this if you have an existing database and need to add the new columns
"""
from sqlalchemy import create_engine, text
import os

# Get database URL
DATABASE_URL = "sqlite:///./data/psi.db"

def migrate_database():
    """Add new columns to existing database if they don't exist"""
    engine = create_engine(DATABASE_URL)
    
    # Check if database file exists
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        print("Database file does not exist. Run init_db.py first.")
        return
    
    with engine.connect() as conn:
        # Check if columns exist and add them if they don't
        try:
            # Check for safety_threshold_percentage
            result = conn.execute(text("PRAGMA table_info(product_models)"))
            columns = [row[1] for row in result]
            
            if 'safety_threshold_percentage' not in columns:
                print("Adding safety_threshold_percentage column...")
                conn.execute(text("ALTER TABLE product_models ADD COLUMN safety_threshold_percentage REAL DEFAULT 20.0"))
                conn.commit()
                print("✓ Added safety_threshold_percentage column")
            else:
                print("✓ safety_threshold_percentage column already exists")
            
            if 'lead_time_weeks' not in columns:
                print("Adding lead_time_weeks column...")
                conn.execute(text("ALTER TABLE product_models ADD COLUMN lead_time_weeks INTEGER DEFAULT 10"))
                conn.commit()
                print("✓ Added lead_time_weeks column")
            else:
                print("✓ lead_time_weeks column already exists")
            
            # Check PurchaseOrder table for new columns
            result = conn.execute(text("PRAGMA table_info(purchase_orders)"))
            po_columns = [row[1] for row in result]
            
            new_po_columns = {
                'forecasted_quantity': 'INTEGER',
                'order_date': 'DATE',
                'expected_delivery_week': 'DATE',
                'stage_updated_at': 'DATETIME'
            }
            
            for col_name, col_type in new_po_columns.items():
                if col_name not in po_columns:
                    print(f"Adding {col_name} column to purchase_orders...")
                    conn.execute(text(f"ALTER TABLE purchase_orders ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    print(f"✓ Added {col_name} column")
                else:
                    print(f"✓ {col_name} column already exists")
            
            print("\n✓ Database migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate_database()

