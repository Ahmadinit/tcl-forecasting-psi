from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, timedelta
from database import get_db
from models import PurchaseOrder, ProductModel, Inventory, SalesRecord
from sqlalchemy import func
from config import settings

router = APIRouter(
    prefix="/purchase",
    tags=["purchase"]
)

class PurchaseOrderCreate(BaseModel):
    product_id: int
    quantity: int
    order_week: date
    etd: Optional[date] = None
    eta: Optional[date] = None
    status: str = "suggested"
    shipping_mode: str = "CKD F"
    stage: Optional[str] = None
    notes: Optional[str] = None

class PurchaseOrderUpdate(BaseModel):
    quantity: Optional[int] = None
    status: Optional[str] = None
    etd: Optional[date] = None
    eta: Optional[date] = None
    stage: Optional[str] = None
    notes: Optional[str] = None

class ForecastRequest(BaseModel):
    product_id: int
    weeks: int = 8

class MessageResponse(BaseModel):
    message: str

# GET: List all purchase orders
@router.get("")
def list_purchase_orders(
    status: Optional[str] = None,
    product_id: Optional[int] = None,
    stage: Optional[str] = None,  # Filter by stage
    db: Session = Depends(get_db)
):
    """Get all purchase orders with filtering by status, product, or stage"""
    query = db.query(PurchaseOrder, ProductModel).join(
        ProductModel, PurchaseOrder.product_id == ProductModel.id
    ).filter(ProductModel.is_active == True)
    
    if status:
        query = query.filter(PurchaseOrder.status == status)
    if product_id:
        query = query.filter(PurchaseOrder.product_id == product_id)
    if stage:
        query = query.filter(PurchaseOrder.stage == stage)
    
    pos = query.order_by(PurchaseOrder.order_week.desc()).all()
    
    return [
        {
            "id": po.id,
            "po_number": po.po_number,
            "product_id": po.product_id,
            "product_name": product.name,
            "product_sku": product.sku,
            "quantity": po.quantity,
            "forecasted_quantity": po.forecasted_quantity,
            "order_week": po.order_week.isoformat(),
            "order_date": po.order_date.isoformat() if po.order_date is not None else None,  # type: ignore[union-attr]
            "expected_delivery_week": po.expected_delivery_week.isoformat() if po.expected_delivery_week is not None else None,  # type: ignore[union-attr]
            "etd": po.etd.isoformat() if po.etd is not None else None,  # type: ignore[union-attr]
            "eta": po.eta.isoformat() if po.eta is not None else None,  # type: ignore[union-attr]
            "status": po.status,
            "shipping_mode": po.shipping_mode,
            "stage": po.stage,
            "stage_updated_at": po.stage_updated_at.isoformat() if po.stage_updated_at is not None else None,  # type: ignore[union-attr]
            "notes": po.notes,
            "created_at": po.created_at.isoformat() if po.created_at is not None else None,  # type: ignore[union-attr]
            "updated_at": po.updated_at.isoformat() if po.updated_at is not None else None  # type: ignore[union-attr]
        }
        for po, product in pos
    ]

# POST: Create purchase order
@router.post("/create")
def create_purchase_order(payload: PurchaseOrderCreate, db: Session = Depends(get_db)):
    """Create a new purchase order"""
    # Check if product exists
    product = db.query(ProductModel).filter(
        ProductModel.id == payload.product_id,
        ProductModel.is_active == True
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Generate PO number automatically
    po_number = f"PO-{date.today().strftime('%Y%m%d')}-{payload.product_id:04d}"
    
    # Calculate ETD and ETA based on Excel Sheet 1 business logic
    # Lead time breakdown:
    # - Order placement: 28 days before ETD (ORDER_ADVANCE_DAYS)
    # - Shipping: 45 days (SHIPPING_DAYS)
    # - Total order to ETD: 28 days (order_week to etd)
    # - ETD to ETA: 45 days shipping + 10 days customs + 15 days production = 70 days
    
    # If ETD not provided, calculate from order_week + 28 days (order placement time)
    if payload.etd is None:
        etd = payload.order_week + timedelta(days=28)  # 28 days after order placement
    else:
        etd = payload.etd
    
    # If ETA not provided, calculate from ETD + lead time (shipping + customs + production)
    if payload.eta is None:
        eta = etd + timedelta(days=settings.LEAD_TIME_DAYS) if etd else None
    else:
        eta = payload.eta
    
    po = PurchaseOrder(
        product_id=payload.product_id,
        po_number=po_number,
        quantity=payload.quantity,
        order_week=payload.order_week,
        etd=etd,
        eta=eta,
        status=payload.status,
        shipping_mode=payload.shipping_mode,
        stage=payload.stage,
        notes=payload.notes
    )
    
    db.add(po)
    db.commit()
    db.refresh(po)
    
    return {
        "id": po.id,
        "po_number": po.po_number,
        "product_id": po.product_id,
        "product_name": product.name,
        "quantity": po.quantity,
        "order_week": po.order_week.isoformat(),
        "etd": po.etd.isoformat() if po.etd is not None else None,  # type: ignore[union-attr]
        "eta": po.eta.isoformat() if po.eta is not None else None,  # type: ignore[union-attr]
        "status": po.status,
        "shipping_mode": po.shipping_mode,
        "stage": po.stage,
        "notes": po.notes
    }

# GET: Forecast purchase order suggestions based on SALES DATA and INVENTORY
@router.get("/forecast")
def forecast_purchase_order(
    product_id: int = Query(..., description="Product ID"),
    weeks: int = Query(8, description="Weeks of historical sales data to use"),
    forecast_weeks: int = Query(10, description="Weeks ahead to forecast (based on lead time)"),
    db: Session = Depends(get_db)
):
    """
    Generate purchase order suggestions based on ACTUAL SALES DATA and CURRENT INVENTORY
    Flow: Sales Data → Forecast Demand → Calculate Required Inventory → Suggest Purchase Quantity → Create PO
    
    Uses weighted moving average of actual sales to predict future demand
    """
    from utils.forecast import ForecastEngine
    from config import settings
    
    # Check if product exists
    product = db.query(ProductModel).filter(
        ProductModel.id == product_id,
        ProductModel.is_active == True
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Use ForecastEngine to generate purchase forecast from sales data
    forecast_engine = ForecastEngine(db)
    forecast_result = forecast_engine.generate_purchase_forecast(product_id, forecast_weeks)
    
    if not forecast_result:
        raise HTTPException(status_code=400, detail="Could not generate forecast")
    
    # Calculate recommended order week (considering lead time)
    # Need to order 28 days before ETD, and ETD is 70 days before we need the stock
    # So order week = today + (forecast_weeks * 7) - 70 - 28
    days_until_needed = forecast_weeks * 7
    recommended_order_week = date.today() + timedelta(days=days_until_needed - settings.ORDER_TO_ETA_DAYS)
    
    # Calculate ETD and ETA based on recommended order week
    recommended_etd = recommended_order_week + timedelta(days=settings.ORDER_ADVANCE_DAYS)
    recommended_eta = recommended_etd + timedelta(days=settings.LEAD_TIME_DAYS)
    
    return {
        "product_id": product_id,
        "product_name": product.name,
        "product_sku": product.sku,
        "current_stock": forecast_result.get("current_stock", 0),
        "forecasted_weekly_demand": forecast_result.get("forecasted_weekly_demand", 0),
        "safety_stock": forecast_result.get("safety_stock", 0),
        "required_inventory": forecast_result.get("required_inventory", 0),
        "suggested_quantity": forecast_result.get("suggested_purchase_quantity", 0),
        "confidence_level": forecast_result.get("confidence_level", "Low"),
        "data_points_used": forecast_result.get("data_points_used", 0),
        "lead_time_days": settings.ORDER_TO_ETA_DAYS,
        "recommended_order_week": recommended_order_week.isoformat(),
        "recommended_etd": recommended_etd.isoformat(),
        "recommended_eta": recommended_eta.isoformat(),
        "calculation_details": {
            "weeks_of_sales_data": weeks,
            "forecast_horizon_weeks": forecast_weeks,
            "order_advance_days": settings.ORDER_ADVANCE_DAYS,
            "shipping_days": settings.SHIPPING_DAYS,
            "total_lead_time_days": settings.LEAD_TIME_DAYS
        }
    }

# PUT: Update purchase order
@router.put("/{po_id}")
def update_purchase_order(po_id: int, payload: PurchaseOrderUpdate, db: Session = Depends(get_db)):
    """Update a purchase order"""
    from datetime import datetime
    
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    # Update fields if provided
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(po, field, value)
    
    # If stage is being updated, record the timestamp
    if payload.stage is not None:
        po.stage_updated_at = datetime.now()  # type: ignore[assignment]
    
    db.commit()
    db.refresh(po)
    
    return {
        "id": po.id,
        "po_number": po.po_number,
        "product_id": po.product_id,
        "quantity": po.quantity,
        "status": po.status,
        "etd": po.etd.isoformat() if po.etd is not None else None,  # type: ignore[union-attr]
        "eta": po.eta.isoformat() if po.eta is not None else None,  # type: ignore[union-attr]
        "stage": po.stage,
        "stage_updated_at": po.stage_updated_at.isoformat() if po.stage_updated_at is not None else None,  # type: ignore[union-attr]
        "notes": po.notes,
        "updated_at": po.updated_at.isoformat() if po.updated_at is not None else None  # type: ignore[union-attr]
    }

# POST: Update PO stage (for interactive slider)
@router.post("/{po_id}/stage")
def update_po_stage(
    po_id: int,
    stage: str = Query(..., description="Stage: CKD Prepared, Booking, Shipped, Customs, Assembly"),
    notes: Optional[str] = Query(None, description="Optional notes for stage change"),
    db: Session = Depends(get_db)
):
    """Update PO stage using interactive slider"""
    from datetime import datetime
    
    valid_stages = ["CKD Prepared", "Booking", "Shipped", "Customs", "Assembly"]
    if stage not in valid_stages:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stage. Must be one of: {', '.join(valid_stages)}"
        )
    
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    po.stage = stage  # type: ignore[assignment]
    po.stage_updated_at = datetime.now()  # type: ignore[assignment]
    if notes:
        po.notes = notes  # type: ignore[assignment]
    
    db.commit()
    db.refresh(po)
    
    return {
        "id": po.id,
        "po_number": po.po_number,
        "stage": po.stage,
        "stage_updated_at": po.stage_updated_at.isoformat() if po.stage_updated_at is not None else None,  # type: ignore[union-attr]
        "message": f"PO stage updated to {stage}"
    }

# POST: Generate weekly POs
@router.post("/generate-weekly")
def generate_weekly_pos(
    order_week: Optional[date] = Query(None, description="Order week (Saturday). If not provided, uses current week"),
    db: Session = Depends(get_db)
):
    """Generate weekly purchase orders for all products (runs on Saturday)"""
    from utils.weekly_po_generator import WeeklyPOGenerator
    
    generator = WeeklyPOGenerator(db)
    # order_week can be None, the function handles it
    result = generator.generate_weekly_pos(order_week)  # type: ignore[arg-type]
    
    return result

# POST: Generate annual POs (52 weeks)
@router.post("/generate-annual")
def generate_annual_pos(
    year: Optional[int] = Query(None, description="Year to generate POs for. If not provided, uses current year"),
    db: Session = Depends(get_db)
):
    """Generate 52 purchase orders per product for a given year"""
    from utils.weekly_po_generator import WeeklyPOGenerator
    
    generator = WeeklyPOGenerator(db)
    # year can be None, the function handles it
    result = generator.generate_annual_pos(year)  # type: ignore[arg-type]
    
    return result

# GET: Get PO timeline data
@router.get("/{po_id}/timeline")
def get_po_timeline(po_id: int, db: Session = Depends(get_db)):
    """Get timeline data for a PO showing weeks from order to delivery"""
    from datetime import timedelta
    
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    # Calculate weeks from order_week to expected_delivery_week
    if po.expected_delivery_week is None:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=400, detail="PO does not have expected delivery week")
    
    order_week = po.order_week  # type: ignore[assignment]
    delivery_week = po.expected_delivery_week  # type: ignore[assignment]
    
    # Generate week boundaries
    weeks = []
    current_week = order_week
    week_num = 0
    
    while current_week <= delivery_week:  # type: ignore[operator]
        week_start = current_week
        week_end = current_week + timedelta(days=6)  # End of week (Friday)
        
        weeks.append({
            "week_number": week_num,
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "date_range": f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
        })
        
        current_week += timedelta(weeks=1)
        week_num += 1
    
    # Map stages to week ranges (approximate)
    stage_weeks = {
        "CKD Prepared": (0, 1),
        "Booking": (1, 2),
        "Shipped": (2, 4),
        "Customs": (4, 5),
        "Assembly": (5, 6)
    }
    
    current_stage = po.stage if po.stage is not None else "CKD Prepared"  # type: ignore[assignment]
    stage_range = stage_weeks.get(current_stage, (0, 1))  # type: ignore[arg-type]
    
    return {
        "po_id": po.id,
        "po_number": po.po_number,
        "order_week": order_week.isoformat(),
        "expected_delivery_week": delivery_week.isoformat(),
        "current_stage": current_stage,
        "stage_range": {
            "start_week": stage_range[0],
            "end_week": stage_range[1]
        },
        "weeks": weeks,
        "total_weeks": len(weeks)
    }

# DELETE: Remove purchase order
@router.delete("/{po_id}")
def delete_purchase_order(po_id: int, db: Session = Depends(get_db)):
    """Delete a purchase order"""
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    db.delete(po)
    db.commit()
    return {"message": "Purchase order deleted successfully"}