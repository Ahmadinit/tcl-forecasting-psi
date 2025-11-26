from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_db
from models import SalesRecord, Inventory, ProductModel

router = APIRouter(
    prefix="/sales",
    tags=["sales"]
)

# Pydantic models
class SalesCreate(BaseModel):
    product_id: int
    quantity: int
    sale_date: Optional[date] = None
    channel: str = "all"  # ecommerce, A101, wholesale, all

class SalesUpdate(BaseModel):
    quantity: Optional[int] = None
    sale_date: Optional[date] = None
    channel: Optional[str] = None

class MessageResponse(BaseModel):
    message: str

# POST: Add sales record
@router.post("")
def add_sale(payload: SalesCreate, db: Session = Depends(get_db)):
    """Add a new sales record and update inventory. Sales only allowed on weekdays (Mon-Fri)."""
    from datetime import datetime
    
    # Set default sale date to today if not provided
    if payload.sale_date is None:
        payload.sale_date = date.today()
    
    # Validate that sale is on a weekday (Monday=0, Sunday=6)
    sale_datetime = datetime.combine(payload.sale_date, datetime.min.time())
    weekday = sale_datetime.weekday()
    if weekday >= 5:  # Saturday (5) or Sunday (6)
        raise HTTPException(
            status_code=400,
            detail="Sales can only be recorded on weekdays (Monday to Friday)"
        )
    
    # Check if product exists and is active
    product = db.query(ProductModel).filter(
        ProductModel.id == payload.product_id,
        ProductModel.is_active == True
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or inactive")
    
    # Check inventory if we're subtracting stock
    inventory = db.query(Inventory).filter(Inventory.product_id == payload.product_id).first()
    if not inventory:
        # Create inventory record if it doesn't exist
        inventory = Inventory(product_id=payload.product_id, current_stock=0)
        db.add(inventory)
        db.flush()
    
    if inventory.current_stock < payload.quantity:  # type: ignore
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient stock. Available: {inventory.current_stock}, Requested: {payload.quantity}"
        )
    
    # Create sales record
    sale = SalesRecord(
        product_id=payload.product_id,
        quantity=payload.quantity,
        sale_date=payload.sale_date,
        channel=payload.channel
    )
    db.add(sale)
    
    # Update inventory (subtract sold quantity) - auto-reduce inventory
    inventory.current_stock -= payload.quantity  # type: ignore[assignment]
    inventory.last_updated = func.now()  # type: ignore[assignment]
    
    db.commit()
    db.refresh(sale)
    
    return {
        "id": sale.id,
        "product_id": sale.product_id,
        "product_name": product.name,
        "quantity": sale.quantity,
        "sale_date": sale.sale_date.isoformat(),
        "channel": sale.channel,
            "created_at": sale.created_at.isoformat() if sale.created_at else None  # type: ignore
    }

# GET: List all sales records
@router.get("")
def list_sales(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    channel: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all sales records with filtering options"""
    query = db.query(SalesRecord)
    
    # Apply filters
    if product_id:
        query = query.filter(SalesRecord.product_id == product_id)
    if start_date:
        query = query.filter(SalesRecord.sale_date >= start_date)
    if end_date:
        query = query.filter(SalesRecord.sale_date <= end_date)
    if channel:
        query = query.filter(SalesRecord.channel == channel)
    
    sales = query.order_by(SalesRecord.sale_date.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": s.id,
            "product_id": s.product_id,
            "product_name": s.product.name if s.product else "Unknown",
            "quantity": s.quantity,
            "sale_date": s.sale_date.isoformat(),
            "channel": s.channel,
            "created_at": s.created_at.isoformat() if s.created_at else None  # type: ignore
        }
        for s in sales
    ]

# GET: Sales by specific model
@router.get("/by_model/{model_id}")
def get_sales_by_model(
    model_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get sales records for a specific product model"""
    # Check if product exists
    product = db.query(ProductModel).filter(
        ProductModel.id == model_id,
        ProductModel.is_active == True
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    query = db.query(SalesRecord).filter(SalesRecord.product_id == model_id)
    
    if start_date:
        query = query.filter(SalesRecord.sale_date >= start_date)
    if end_date:
        query = query.filter(SalesRecord.sale_date <= end_date)
    
    sales = query.order_by(SalesRecord.sale_date.desc()).all()
    
    return [
        {
            "id": s.id,
            "quantity": s.quantity,
            "sale_date": s.sale_date.isoformat(),
            "channel": s.channel,
            "created_at": s.created_at.isoformat() if s.created_at else None  # type: ignore
        }
        for s in sales
    ]

# GET: Sales summary by product
@router.get("/summary")
def get_sales_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get sales summary grouped by product"""
    query = db.query(
        SalesRecord.product_id,
        ProductModel.name,
        ProductModel.sku,
        func.sum(SalesRecord.quantity).label('total_quantity'),
        func.count(SalesRecord.id).label('sales_count')
    ).join(ProductModel).filter(ProductModel.is_active == True)
    
    if start_date:
        query = query.filter(SalesRecord.sale_date >= start_date)
    if end_date:
        query = query.filter(SalesRecord.sale_date <= end_date)
    
    summary = query.group_by(SalesRecord.product_id, ProductModel.name, ProductModel.sku).all()
    
    return [
        {
            "product_id": item.product_id,
            "product_name": item.name,
            "sku": item.sku,
            "total_quantity": item.total_quantity,
            "sales_count": item.sales_count
        }
        for item in summary
    ]

# GET: Weekly sales data for forecasting
@router.get("/weekly")
def get_weekly_sales(
    product_id: int,
    weeks: int = 8,  # Get last 8 weeks of data for forecasting
    db: Session = Depends(get_db)
):
    """Get weekly sales data for forecasting calculations"""
    from datetime import timedelta
    
    end_date = date.today()
    start_date = end_date - timedelta(weeks=weeks)
    
    # This is a simplified version - in production you'd use proper week grouping
    sales = db.query(SalesRecord).filter(
        SalesRecord.product_id == product_id,
        SalesRecord.sale_date >= start_date,
        SalesRecord.sale_date <= end_date
    ).order_by(SalesRecord.sale_date).all()
    
    # Group by week (simplified)
    weekly_data = {}
    for sale in sales:
        # Simple week grouping - in real app use proper week numbers
        week_key = sale.sale_date.isocalendar()[1]  # Week number
        if week_key not in weekly_data:
            weekly_data[week_key] = 0
        weekly_data[week_key] += sale.quantity
    
    return {
        "product_id": product_id,
        "weeks": weeks,
        "weekly_sales": [
            {"week": week, "quantity": quantity}
            for week, quantity in weekly_data.items()
        ]
    }

# PUT: Update sales record
@router.put("/{sale_id}")
def update_sale(sale_id: int, payload: SalesUpdate, db: Session = Depends(get_db)):
    """Update a sales record"""
    sale = db.query(SalesRecord).filter(SalesRecord.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sales record not found")
    
    # Calculate quantity difference for inventory adjustment
    old_quantity = sale.quantity
    quantity_diff = 0
    
    if payload.quantity is not None and payload.quantity != old_quantity:
        quantity_diff = payload.quantity - old_quantity
        sale.quantity = payload.quantity  # type: ignore
    
    if payload.sale_date is not None:
        sale.sale_date = payload.sale_date  # type: ignore
    
    if payload.channel is not None:
        sale.channel = payload.channel  # type: ignore
    
    # Update inventory if quantity changed
    if quantity_diff != 0:  # type: ignore
        inventory = db.query(Inventory).filter(Inventory.product_id == sale.product_id).first()
        if inventory:
            new_stock = inventory.current_stock - quantity_diff  # type: ignore
            if new_stock < 0:  # type: ignore
                raise HTTPException(status_code=400, detail="Inventory would go negative with this update")
            inventory.current_stock = new_stock  # type: ignore
    
    db.commit()
    db.refresh(sale)
    
    return {
        "id": sale.id,
        "product_id": sale.product_id,
        "quantity": sale.quantity,
        "sale_date": sale.sale_date.isoformat(),
        "channel": sale.channel
    }

# DELETE: Remove sales record
@router.delete("/{sale_id}")
def delete_sales_record(sale_id: int, db: Session = Depends(get_db)):
    """Delete a sales record and restore inventory"""
    sale = db.query(SalesRecord).filter(SalesRecord.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sales record not found")
    
    # Restore inventory
    inventory = db.query(Inventory).filter(Inventory.product_id == sale.product_id).first()
    if inventory:
        inventory.current_stock += sale.quantity  # type: ignore
    
    db.delete(sale)
    db.commit()
    
    return {"message": "Sales record deleted successfully and inventory restored"}