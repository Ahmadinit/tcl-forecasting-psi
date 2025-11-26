from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
from models import SystemConfig

router = APIRouter(
    prefix="/settings",
    tags=["settings"]
)

class SettingUpdate(BaseModel):
    config_value: str

class SettingCreate(BaseModel):
    config_key: str
    config_value: str
    description: Optional[str] = None

class MessageResponse(BaseModel):
    message: str

# GET: Get all settings
@router.get("")
def get_settings(db: Session = Depends(get_db)):
    """Get all system settings with defaults"""
    from config import settings as app_settings
    
    # Get all settings from database
    db_settings = db.query(SystemConfig).all()
    settings_dict = {s.config_key: s.config_value for s in db_settings}
    
    # Return with defaults if not in database
    default_settings = {
        "default_safety_threshold": "20.0",  # 20%
        "default_lead_time_weeks": "10",
        "business_days": "5",  # Monday-Friday
        "financial_year_start": "2025-01-01",
        "low_stock_alerts_enabled": "true",
        "auto_po_suggestions_enabled": "true"
    }
    
    result = []
    for key, default_value in default_settings.items():
        result.append({
            "config_key": key,
            "config_value": settings_dict.get(key, default_value),  # type: ignore
            "description": f"Default: {default_value}"
        })
    
    # Add any additional settings from database
    for s in db_settings:
        if s.config_key not in default_settings:
            result.append({
                "config_key": s.config_key,
                "config_value": s.config_value,
                "description": s.description,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None  # type: ignore
            })
    
    return result

# GET: Get specific setting
@router.get("/{config_key}")
def get_setting(config_key: str, db: Session = Depends(get_db)):
    """Get a specific system setting"""
    setting = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    return {
        "id": setting.id,
        "config_key": setting.config_key,
        "config_value": setting.config_value,
        "description": setting.description,
        "updated_at": setting.updated_at.isoformat() if setting.updated_at else None  # type: ignore
    }

# PUT: Update setting (creates if doesn't exist)
@router.put("/{config_key}")
def update_setting(config_key: str, payload: SettingUpdate, db: Session = Depends(get_db)):
    """Update a system setting. Creates if it doesn't exist."""
    setting = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    
    if not setting:
        # Create new setting
        setting = SystemConfig(
            config_key=config_key,
            config_value=payload.config_value,
            description=f"System setting: {config_key}"
        )
        db.add(setting)
    else:
        setting.config_value = payload.config_value  # type: ignore
    
    db.commit()
    db.refresh(setting)
    
    return {
        "message": "Setting updated successfully",
        "config_key": setting.config_key,
        "config_value": setting.config_value,
        "updated_at": setting.updated_at.isoformat() if setting.updated_at else None  # type: ignore
    }

# POST: Update multiple settings at once
@router.post("/bulk-update")
def bulk_update_settings(
    settings: dict,
    db: Session = Depends(get_db)
):
    """Update multiple settings at once"""
    updated = []
    for key, value in settings.items():
        setting = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        
        if not setting:
            setting = SystemConfig(
                config_key=key,
                config_value=str(value),
                description=f"System setting: {key}"
            )
            db.add(setting)
        else:
            setting.config_value = str(value)  # type: ignore
        
        updated.append(key)
    
    db.commit()
    
    return {
        "message": f"Updated {len(updated)} settings",
        "updated_keys": updated
    }

# POST: Create new setting
@router.post("")
def create_setting(payload: SettingCreate, db: Session = Depends(get_db)):
    """Create a new system setting"""
    existing = db.query(SystemConfig).filter(SystemConfig.config_key == payload.config_key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Setting already exists")
    
    setting = SystemConfig(
        config_key=payload.config_key,
        config_value=payload.config_value,
        description=payload.description
    )
    db.add(setting)
    db.commit()
    db.refresh(setting)
    
    return {
        "message": "Setting created successfully",
        "id": setting.id,
        "config_key": setting.config_key,
        "config_value": setting.config_value,
        "description": setting.description
    }

# DELETE: Delete setting
@router.delete("/{config_key}")
def delete_setting(config_key: str, db: Session = Depends(get_db)):
    """Delete a system setting"""
    setting = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    db.delete(setting)
    db.commit()
    return {"message": "Setting deleted successfully"}

# GET: Lead time settings (convenience endpoint)
@router.get("/lead-times/summary")
def get_lead_time_summary(db: Session = Depends(get_db)):
    """Get lead time settings summary"""
    lead_time_settings = db.query(SystemConfig).filter(
        SystemConfig.config_key.like('lead_time_%')
    ).all()
    
    summary = {}
    for setting in lead_time_settings:
        key = setting.config_key.replace('lead_time_', '')
        summary[key] = {
            "days": int(setting.config_value),  # type: ignore
            "description": setting.description
        }
    
    return summary