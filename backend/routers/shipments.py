from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from database import get_db
from models import PurchaseOrder, ProductModel

router = APIRouter(
    prefix="/shipments",
    tags=["shipments"]
)

class ShipmentUpdate(BaseModel):
    stage: str
    notes: Optional[str] = None
    etd: Optional[date] = None
    eta: Optional[date] = None

class MessageResponse(BaseModel):
    message: str

# Shipment stages based on Excel business logic
SHIPMENT_STAGES = [
    "CKD Materials Prepared",
    "Booking Confirmed", 
    "Shipped",
    "Customs Clearance",
    "Assembly",
    "CBU Warehouse"
]

# GET: List all shipments
@router.get("")
def list_shipments(
    stage: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all shipments with tracking information"""
    query = db.query(PurchaseOrder, ProductModel).join(
        ProductModel, PurchaseOrder.product_id == ProductModel.id
    ).filter(ProductModel.is_active == True)
    
    if stage:
        query = query.filter(PurchaseOrder.stage == stage)
    if status:
        query = query.filter(PurchaseOrder.status == status)
    
    shipments = query.order_by(PurchaseOrder.order_week.desc()).all()
    
    return [
        {
            "id": po.id,
            "po_number": po.po_number,
            "product_id": po.product_id,
            "product_name": product.name,
            "product_sku": product.sku,
            "quantity": po.quantity,
            "order_week": po.order_week.isoformat(),
            "etd": po.etd.isoformat() if po.etd else None,
            "eta": po.eta.isoformat() if po.eta else None,
            "status": po.status,
            "current_stage": po.stage or "Not Started",
            "notes": po.notes,
            "shipping_mode": po.shipping_mode,
            "updated_at": po.updated_at.isoformat() if po.updated_at else None
        }
        for po, product in shipments
    ]

# POST: Update shipment stage
@router.post("/update-stage")
def update_shipment_stage(
    po_id: int = Query(..., description="Purchase Order ID"),
    stage: str = Query(..., description="New shipment stage"),
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update shipment stage for a purchase order"""
    if stage not in SHIPMENT_STAGES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid stage. Must be one of: {', '.join(SHIPMENT_STAGES)}"
        )
    
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    po.stage = stage  # type: ignore
    if notes:
        po.notes = notes  # type: ignore
    
    # Update status based on stage
    if stage == "CBU Warehouse":
        po.status = "delivered"  # type: ignore
    elif stage in ["Shipped", "Customs Clearance", "Assembly"]:
        po.status = "shipped"  # type: ignore
    else:
        po.status = "ordered"  # type: ignore
    
    db.commit()
    db.refresh(po)
    
    return {
        "message": f"Shipment stage updated to {stage}",
        "po_id": po.id,
        "current_stage": po.stage,
        "status": po.status,
        "notes": po.notes
    }

# GET: Shipment status by PO
@router.get("/status/{po_id}")
def get_shipment_status(po_id: int, db: Session = Depends(get_db)):
    """Get detailed shipment status for a specific PO"""
    po = db.query(PurchaseOrder, ProductModel).join(
        ProductModel, PurchaseOrder.product_id == ProductModel.id
    ).filter(PurchaseOrder.id == po_id).first()
    
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    purchase_order, product = po
    
    # Calculate progress percentage based on stage
    stage_index = SHIPMENT_STAGES.index(purchase_order.stage) if purchase_order.stage in SHIPMENT_STAGES else -1
    progress = round(((stage_index + 1) / len(SHIPMENT_STAGES)) * 100) if stage_index >= 0 else 0
    
    return {
        "po_id": purchase_order.id,
        "po_number": purchase_order.po_number,
        "product_name": product.name,
        "product_sku": product.sku,
        "quantity": purchase_order.quantity,
        "current_stage": purchase_order.stage or "Not Started",
        "progress_percentage": progress,
        "etd": purchase_order.etd.isoformat() if purchase_order.etd else None,
        "eta": purchase_order.eta.isoformat() if purchase_order.eta else None,
        "status": purchase_order.status,
        "notes": purchase_order.notes,
        "shipping_mode": purchase_order.shipping_mode,
        "all_stages": SHIPMENT_STAGES,
        "updated_at": purchase_order.updated_at.isoformat() if purchase_order.updated_at else None
    }

# GET: Shipment timeline
@router.get("/timeline")
def get_shipment_timeline(
    product_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get shipment timeline for all or specific products"""
    query = db.query(PurchaseOrder, ProductModel).join(
        ProductModel, PurchaseOrder.product_id == ProductModel.id
    ).filter(ProductModel.is_active == True)
    
    if product_id:
        query = query.filter(PurchaseOrder.product_id == product_id)
    
    shipments = query.order_by(PurchaseOrder.eta.desc()).all()
    
    return [
        {
            "po_id": po.id,
            "po_number": po.po_number,
            "product_id": po.product_id,
            "product_name": product.name,
            "quantity": po.quantity,
            "current_stage": po.stage or "Not Started",
            "etd": po.etd.isoformat() if po.etd else None,
            "eta": po.eta.isoformat() if po.eta else None,
            "status": po.status,
            "days_until_eta": (po.eta - date.today()).days if po.eta else None,
            "shipping_mode": po.shipping_mode
        }
        for po, product in shipments
    ]