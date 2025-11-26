from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import ProductModel
import schemas

router = APIRouter(
    prefix="/models",
    tags=["models"]
)

# Pydantic model for request
class ProductModelCreate(BaseModel):
    sku: str
    name: str
    shipping_mode: str = "CKD F"
    status: str = "2025 Product"
    remarks: Optional[str] = None
    safety_stock_days: int = 45
    safety_threshold_percentage: float = 20.0  # Safety stock as % of current inventory
    lead_time_weeks: int = 10  # Lead time in weeks

@router.post("")
def create_model(payload: ProductModelCreate, db: Session = Depends(get_db)):
    """Create a new product model"""
    try:
        existing = db.query(ProductModel).filter(ProductModel.sku == payload.sku).first()
        if existing:
            raise HTTPException(status_code=400, detail="SKU already exists")
        
        # Validate and clean input
        sku = payload.sku.strip() if payload.sku else ""
        name = payload.name.strip() if payload.name else ""
        
        if not sku or not name:
            raise HTTPException(status_code=400, detail="SKU and Name are required")
        
        new_model = ProductModel(
            sku=sku,
            name=name,
            shipping_mode=payload.shipping_mode,
            status=payload.status,
            remarks=payload.remarks.strip() if payload.remarks and payload.remarks.strip() else None,  # Handle empty strings
            safety_stock_days=payload.safety_stock_days,
            safety_threshold_percentage=payload.safety_threshold_percentage,
            lead_time_weeks=payload.lead_time_weeks
        )
        db.add(new_model)
        db.flush()  # Flush to get the ID without committing
        
        # Also create inventory record for the new product
        from models import Inventory
        # Check if inventory already exists
        existing_inventory = db.query(Inventory).filter(Inventory.product_id == new_model.id).first()
        if not existing_inventory:
            inventory = Inventory(
                product_id=new_model.id,
                current_stock=0,
                cbu_in_hand=0,
                kits_in_factory=0
            )
            db.add(inventory)
        
        db.commit()
        db.refresh(new_model)
        
        return {
            "id": new_model.id,
            "sku": new_model.sku,
            "name": new_model.name,
            "shipping_mode": new_model.shipping_mode,
            "status": new_model.status,
            "remarks": new_model.remarks,
            "safety_stock_days": new_model.safety_stock_days,
            "safety_threshold_percentage": new_model.safety_threshold_percentage,  # type: ignore
            "lead_time_weeks": new_model.lead_time_weeks,  # type: ignore
            "is_active": new_model.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = f"Failed to create model: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("")
def list_models(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """List all product models"""
    query = db.query(ProductModel)
    if active_only:
        query = query.filter(ProductModel.is_active == True)
    
    models = query.all()
    return [
        {
            "id": m.id,
            "sku": m.sku,
            "name": m.name,
            "shipping_mode": m.shipping_mode,
            "status": m.status,
            "remarks": m.remarks,
            "safety_stock_days": m.safety_stock_days,
            "safety_threshold_percentage": m.safety_threshold_percentage if m.safety_threshold_percentage is not None else 20.0,  # type: ignore
            "lead_time_weeks": m.lead_time_weeks if m.lead_time_weeks is not None else 10,  # type: ignore
            "is_active": m.is_active,
            "created_at": m.created_at.isoformat() if m.created_at is not None else None  # type: ignore[union-attr]
        }
        for m in models
    ]

@router.put("/{model_id}")
def update_model(model_id: int, payload: ProductModelCreate, db: Session = Depends(get_db)):
    """Update a product model"""
    try:
        model = db.query(ProductModel).filter(ProductModel.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Check SKU uniqueness if changed
        if payload.sku != model.sku:  # type: ignore[comparison-overlap]
            existing = db.query(ProductModel).filter(
                ProductModel.sku == payload.sku,
                ProductModel.id != model_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="SKU already exists")
        
        # Validate and clean input
        sku = payload.sku.strip() if payload.sku else ""
        name = payload.name.strip() if payload.name else ""
        
        if not sku or not name:
            raise HTTPException(status_code=400, detail="SKU and Name are required")
        
        model.sku = sku  # type: ignore[assignment]
        model.name = name  # type: ignore[assignment]
        model.shipping_mode = payload.shipping_mode  # type: ignore[assignment]
        model.status = payload.status  # type: ignore[assignment]
        model.remarks = payload.remarks.strip() if payload.remarks and payload.remarks.strip() else None  # type: ignore[assignment]
        model.safety_stock_days = payload.safety_stock_days  # type: ignore[assignment]
        model.safety_threshold_percentage = payload.safety_threshold_percentage  # type: ignore[assignment]
        model.lead_time_weeks = payload.lead_time_weeks  # type: ignore[assignment]
        
        db.commit()
        db.refresh(model)
        
        return {
            "id": model.id,
            "sku": model.sku,
            "name": model.name,
            "shipping_mode": model.shipping_mode,
            "status": model.status,
            "remarks": model.remarks,
            "safety_stock_days": model.safety_stock_days,
            "safety_threshold_percentage": model.safety_threshold_percentage,  # type: ignore
            "lead_time_weeks": model.lead_time_weeks,  # type: ignore
            "is_active": model.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update model: {str(e)}")

@router.delete("/{model_id}")
def delete_model(model_id: int, db: Session = Depends(get_db)):
    """Soft delete a product model"""
    model = db.query(ProductModel).filter(ProductModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model.is_active = False  # type: ignore[assignment]
    db.commit()
    return {"message": "Model deleted successfully"}

@router.get("/{model_id}")
def get_model(model_id: int, db: Session = Depends(get_db)):
    """Get a specific product model"""
    model = db.query(ProductModel).filter(ProductModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return {
        "id": model.id,
        "sku": model.sku,
        "name": model.name,
        "shipping_mode": model.shipping_mode,
        "status": model.status,
        "remarks": model.remarks,
        "safety_stock_days": model.safety_stock_days,
        "safety_threshold_percentage": model.safety_threshold_percentage if model.safety_threshold_percentage is not None else 20.0,  # type: ignore
        "lead_time_weeks": model.lead_time_weeks if model.lead_time_weeks is not None else 10,  # type: ignore
        "is_active": model.is_active,
        "created_at": model.created_at.isoformat() if model.created_at is not None else None  # type: ignore[union-attr]
    }