from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from database import get_db
from models import Inventory, ProductModel
from utils.calculations import BusinessCalculations
from utils.forecast import ForecastEngine

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"]
)

class InventoryUpdate(BaseModel):
    product_id: int
    current_stock: int = 0
    cbu_in_hand: int = 0
    kits_in_factory: int = 0

class ProductConfigUpdate(BaseModel):
    """Update product-specific configuration (safety threshold, lead time)"""
    product_id: int
    safety_threshold_percentage: Optional[float] = None  # Safety stock as % of current inventory
    lead_time_weeks: Optional[int] = None  # Lead time in weeks

class InventorySubtract(BaseModel):
    product_id: int
    quantity: int

class MessageResponse(BaseModel):
    message: str

# GET: Get all inventory levels with product details
@router.get("/")
def get_inventory(
    low_stock_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all inventory levels with product information"""
    query = db.query(Inventory, ProductModel).join(
        ProductModel, Inventory.product_id == ProductModel.id
    ).filter(ProductModel.is_active == True)
    
    if low_stock_only:
        query = query.filter(Inventory.current_stock <= ProductModel.safety_stock_days)
    
    inventory_data = query.all()
    
    return [
        {
            "id": inv.id,
            "product_id": inv.product_id,
            "product_name": product.name,
            "product_sku": product.sku,
            "current_stock": inv.current_stock,
            "cbu_in_hand": inv.cbu_in_hand,
            "kits_in_factory": inv.kits_in_factory,
            "safety_stock_days": product.safety_stock_days,
            "stock_status": "Low" if inv.current_stock <= product.safety_stock_days else "Adequate",
            "last_updated": inv.last_updated.isoformat() if inv.last_updated else None
        }
        for inv, product in inventory_data
    ]

# GET: Get specific inventory item
@router.get("/{product_id}")
def get_inventory_item(product_id: int, db: Session = Depends(get_db)):
    """Get inventory for a specific product"""
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    
    return {
        "id": inventory.id,
        "product_id": inventory.product_id,
        "product_name": product.name if product else "Unknown",
        "product_sku": product.sku if product else "Unknown",
        "current_stock": inventory.current_stock,
        "cbu_in_hand": inventory.cbu_in_hand,
        "kits_in_factory": inventory.kits_in_factory,
        "safety_stock_days": product.safety_stock_days if product else 0,  # type: ignore
        "stock_status": "Low" if (inventory.current_stock or 0) <= (product.safety_stock_days if product else 0) else "Adequate",  # type: ignore[operator]
        "last_updated": inventory.last_updated.isoformat() if inventory.last_updated else None  # type: ignore[union-attr]
    }

# POST: Update inventory
@router.post("/update")
def update_inventory(payload: InventoryUpdate, db: Session = Depends(get_db)):
    """Update inventory for a product"""
    # Check if product exists
    product = db.query(ProductModel).filter(
        ProductModel.id == payload.product_id,
        ProductModel.is_active == True
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    inventory = db.query(Inventory).filter(Inventory.product_id == payload.product_id).first()
    if inventory:  # type: ignore[truthy-function]
        inventory.current_stock = payload.current_stock  # type: ignore[assignment]
        inventory.cbu_in_hand = payload.cbu_in_hand  # type: ignore[assignment]
        inventory.kits_in_factory = payload.kits_in_factory  # type: ignore[assignment]
    else:
        inventory = Inventory(
            product_id=payload.product_id,
            current_stock=payload.current_stock,
            cbu_in_hand=payload.cbu_in_hand,
            kits_in_factory=payload.kits_in_factory
        )
        db.add(inventory)
    
    db.commit()
    db.refresh(inventory)
    
    return {
        "id": inventory.id,
        "product_id": inventory.product_id,
        "current_stock": inventory.current_stock,
        "cbu_in_hand": inventory.cbu_in_hand,
        "kits_in_factory": inventory.kits_in_factory,
        "message": "Inventory updated successfully"
    }

# PUT: Update product configuration (safety threshold, lead time)
@router.put("/product-config")
def update_product_config(payload: ProductConfigUpdate, db: Session = Depends(get_db)):
    """Update product-specific safety threshold percentage and lead time"""
    product = db.query(ProductModel).filter(
        ProductModel.id == payload.product_id,
        ProductModel.is_active == True
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if payload.safety_threshold_percentage is not None:
        if payload.safety_threshold_percentage < 0 or payload.safety_threshold_percentage > 100:
            raise HTTPException(status_code=400, detail="Safety threshold must be between 0 and 100")
        product.safety_threshold_percentage = payload.safety_threshold_percentage  # type: ignore[assignment]
    
    if payload.lead_time_weeks is not None:
        if payload.lead_time_weeks < 1:
            raise HTTPException(status_code=400, detail="Lead time must be at least 1 week")
        product.lead_time_weeks = payload.lead_time_weeks  # type: ignore[assignment]
    
    db.commit()
    db.refresh(product)
    
    return {
        "product_id": product.id,
        "product_sku": product.sku,
        "safety_threshold_percentage": product.safety_threshold_percentage,  # type: ignore
        "lead_time_weeks": product.lead_time_weeks,  # type: ignore
        "message": "Product configuration updated successfully"
    }

# POST: Subtract from inventory
@router.post("/subtract")
def subtract_inventory(payload: InventorySubtract, db: Session = Depends(get_db)):
    """Subtract quantity from inventory (for sales)"""
    inventory = db.query(Inventory).filter(Inventory.product_id == payload.product_id).first()
    if not inventory:  # type: ignore[truthy-function]
        raise HTTPException(status_code=404, detail="Inventory record not found")
    
    current_stock: int = inventory.current_stock or 0  # type: ignore
    if current_stock < payload.quantity:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient stock. Available: {current_stock}, Requested: {payload.quantity}"
        )
    
    inventory.current_stock = current_stock - payload.quantity  # type: ignore[assignment]
    db.commit()
    
    return {
        "message": "Inventory subtracted successfully",
        "remaining_stock": inventory.current_stock
    }

# GET: Low stock alerts
@router.get("/alerts/low-stock")
def get_low_stock_alerts(db: Session = Depends(get_db)):
    """Get products with low stock (below safety stock)"""
    low_stock_items = db.query(Inventory, ProductModel).join(
        ProductModel, Inventory.product_id == ProductModel.id
    ).filter(
        Inventory.current_stock <= ProductModel.safety_stock_days,
        ProductModel.is_active == True
    ).all()
    
    return [
        {
            "product_id": inv.product_id,
            "product_name": product.name,
            "product_sku": product.sku,
            "current_stock": inv.current_stock,
            "safety_stock_days": product.safety_stock_days,
            "stock_deficit": product.safety_stock_days - inv.current_stock,
            "status": "Critical" if inv.current_stock == 0 else "Low"
        }
        for inv, product in low_stock_items
    ]

# DELETE: Remove inventory record
@router.delete("/{product_id}")
def delete_inventory_record(product_id: int, db: Session = Depends(get_db)):
    """Delete inventory record for a product"""
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    
    db.delete(inventory)
    db.commit()
    return {"message": "Inventory record deleted successfully"}

# GET: Calculate monthly PSI (Excel Sheet 2)
@router.get("/psi/monthly")
def calculate_monthly_psi(
    product_id: int = Query(..., description="Product ID"),
    target_month: date = Query(..., description="Target month (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Calculate monthly PSI metrics based on Excel Sheet 2 formulas
    - Available Sales Inventory = SUM(Weekly Purchases) + Previous Month Ending Inventory
    - Ending Inventory = Available Sales Inventory - Monthly Sales Forecast
    - DOS Days = (Ending Inventory / Monthly Sales Forecast) * 30
    """
    calculations = BusinessCalculations(db)
    result = calculations.calculate_monthly_psi(product_id, target_month)
    
    if not result:
        raise HTTPException(status_code=404, detail="Product not found or calculation failed")
    
    return result

# GET: Calculate N+3 rolling stock (Excel Sheet 3)
@router.get("/n-plus-3-stock")
def calculate_n_plus_3_stock(
    product_id: int = Query(..., description="Product ID"),
    db: Session = Depends(get_db)
):
    """
    Calculate N+3 rolling stock projection based on Excel Sheet 3
    End-to-End Inventory = Branch finished goods + Factory kits + Sea shipping + Domestic ODF
    """
    try:
        calculations = BusinessCalculations(db)
        result = calculations.calculate_n_plus_3_stock(product_id)
        
        if not result or result == {}:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found or calculation failed")
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

# GET: Multi-channel sales aggregation (Excel Sheet 4)
@router.get("/sales/multi-channel")
def get_multi_channel_sales(
    product_id: int = Query(..., description="Product ID"),
    target_month: date = Query(..., description="Target month (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get multi-channel sales forecast aggregation based on Excel Sheet 4
    Channels: E-commerce + A101 + Traditional wholesale
    """
    forecast_engine = ForecastEngine(db)
    result = forecast_engine.aggregate_multi_channel_sales(product_id, target_month)
    
    return result