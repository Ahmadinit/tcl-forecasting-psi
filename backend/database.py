from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys

# Determine if running as bundled executable (PyInstaller)
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    if sys.platform == 'darwin':  # macOS
        # Use app support directory for bundled app
        app_support = os.path.expanduser('~/Library/Application Support/PSI Forecast System')
        data_dir = os.path.join(app_support, 'data')
    elif sys.platform == 'win32':  # Windows
        app_data = os.path.expanduser('~/AppData/Roaming/PSI Forecast System')
        data_dir = os.path.join(app_data, 'data')
    else:  # Linux
        app_data = os.path.expanduser('~/.local/share/psi-forecast-system')
        data_dir = os.path.join(app_data, 'data')
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, 'psi.db')
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
else:
    # Running as script (development)
    # Database URL - using SQLite for development
    SQLALCHEMY_DATABASE_URL = "sqlite:///./data/psi.db"
    # For production, you might use: 
    # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/psi_db"

    # Create data directory if it doesn't exist
    # Get the directory where this file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Export DATABASE_URL for migration script
DATABASE_URL = SQLALCHEMY_DATABASE_URL

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    from models import Base
    Base.metadata.create_all(bind=engine)
