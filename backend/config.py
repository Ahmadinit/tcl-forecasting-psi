import os
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PSI Forecast System"
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/psi.db"
    
    # Forecasting Settings (from Excel business logic)
    FORECAST_WEIGHTS: List[float] = [0.5, 0.3, 0.15, 0.05]  # Weighted moving average (Excel Sheet 4)
    
    # Lead Time Settings (from Excel Sheet 1: "purchase FCST")
    # Total lead time breakdown: 73 days (28 + 45) from order to ETD, then 70 days to ETA
    ORDER_ADVANCE_DAYS: int = 28  # Days before ETD to place order (F3-28 in Excel)
    SHIPPING_DAYS: int = 45       # Sea freight duration (F3+45 in Excel)
    CUSTOMS_DAYS: int = 10        # Customs clearance  
    PRODUCTION_DAYS: int = 15     # Assembly to warehouse
    LEAD_TIME_DAYS: int = 70      # Total lead time (ETD to ETA: shipping + customs + production)
    ORDER_TO_ETD_DAYS: int = 28   # Order week to ETD (from Sheet 1)
    ORDER_TO_ETA_DAYS: int = 73   # Order week to ETA (28 order + 45 shipping, from Sheet 1)
    
    # Inventory Settings
    TARGET_DOS_NEW: tuple = (50, 60)      # DOS range for new branches
    TARGET_DOS_ESTABLISHED: tuple = (0, 45) # DOS range for established branches
    SERVICE_LEVEL: float = 0.95           # Service level for safety stock
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()