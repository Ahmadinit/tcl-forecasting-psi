"""
Dashboard router with charts and metrics
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import date, timedelta, datetime
from database import get_db
from models import ProductModel, Inventory, SalesRecord, PurchaseOrder, SystemConfig

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

# GET: Dashboard statistics and metrics
@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics: total products, critical products, pending POs, weekly sales"""
    # Total products
    total_products = db.query(ProductModel).filter(ProductModel.is_active == True).count()
    
    # Get inventory data first
    inventory_data = db.query(Inventory, ProductModel).join(
        ProductModel, Inventory.product_id == ProductModel.id
    ).filter(ProductModel.is_active == True).all()
    
    # Critical products (below safety stock) - calculate manually due to SQL limitations
    critical_products = 0
    for inv, product in inventory_data:
        current_stock = inv.current_stock if inv.current_stock is not None else 0  # type: ignore
        safety_threshold = product.safety_threshold_percentage if product.safety_threshold_percentage is not None else 20.0  # type: ignore
        safety_stock = int(current_stock * (safety_threshold / 100.0))
        
        if current_stock <= safety_stock:
            critical_products += 1
    
    # Warning products (within 20% above safety stock)
    
    warning_count = 0
    for inv, product in inventory_data:
        current_stock = inv.current_stock if inv.current_stock is not None else 0  # type: ignore
        safety_threshold = product.safety_threshold_percentage if product.safety_threshold_percentage is not None else 20.0  # type: ignore
        safety_stock = int(current_stock * (safety_threshold / 100.0))
        warning_threshold = int(safety_stock * 1.2)  # 20% above safety stock
        
        if current_stock > safety_stock and current_stock <= warning_threshold:
            warning_count += 1
    
    # Pending POs (suggested or ordered)
    pending_pos = db.query(PurchaseOrder).filter(
        PurchaseOrder.status.in_(["suggested", "ordered"])
    ).count()
    
    # Current week sales (Monday to Friday)
    today = date.today()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=4)  # Friday
    
    weekly_sales = db.query(func.sum(SalesRecord.quantity)).filter(
        and_(
            SalesRecord.sale_date >= week_start,
            SalesRecord.sale_date <= week_end
        )
    ).scalar() or 0
    
    return {
        "total_products": total_products,
        "critical_products": critical_products,
        "warning_products": warning_count,
        "safe_products": total_products - critical_products - warning_count,
        "pending_pos": pending_pos,
        "weekly_sales": int(weekly_sales),
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat()
    }

# GET: Inventory health pie chart data
@router.get("/charts/inventory-health")
def get_inventory_health_chart(db: Session = Depends(get_db)):
    """Get data for inventory health pie chart (critical, warning, safe)"""
    inventory_data = db.query(Inventory, ProductModel).join(
        ProductModel, Inventory.product_id == ProductModel.id
    ).filter(ProductModel.is_active == True).all()
    
    critical = 0
    warning = 0
    safe = 0
    
    for inv, product in inventory_data:
        current_stock = inv.current_stock if inv.current_stock is not None else 0  # type: ignore
        safety_threshold = product.safety_threshold_percentage if product.safety_threshold_percentage is not None else 20.0  # type: ignore
        safety_stock = int(current_stock * (safety_threshold / 100.0))
        warning_threshold = int(safety_stock * 1.2)  # 20% above safety stock
        
        if current_stock <= safety_stock:
            critical += 1
        elif current_stock <= warning_threshold:
            warning += 1
        else:
            safe += 1
    
    return {
        "labels": ["Critical", "Warning", "Safe"],
        "data": [critical, warning, safe],
        "colors": ["#f44336", "#ff9800", "#4caf50"]
    }

# GET: Sales trend line chart data
@router.get("/charts/sales-trend")
def get_sales_trend_chart(
    weeks: int = Query(12, description="Number of weeks to show"),
    product_id: Optional[int] = Query(None, description="Filter by product"),
    db: Session = Depends(get_db)
):
    """Get sales trend data for line chart"""
    end_date = date.today()
    start_date = end_date - timedelta(weeks=weeks)
    
    # SQLite doesn't have date_trunc, so we'll group by week manually
    query = db.query(SalesRecord).filter(
        SalesRecord.sale_date >= start_date,
        SalesRecord.sale_date <= end_date
    )
    
    if product_id:
        query = query.filter(SalesRecord.product_id == product_id)
    
    sales_records = query.all()
    
    # Group by week (Monday of each week)
    weekly_sales = {}
    for sale in sales_records:
        sale_date = sale.sale_date
        days_since_monday = sale_date.weekday()
        week_monday = sale_date - timedelta(days=days_since_monday)
        week_key = week_monday.isoformat()
        
        if week_key not in weekly_sales:
            weekly_sales[week_key] = 0
        weekly_sales[week_key] += sale.quantity if sale.quantity is not None else 0  # type: ignore
    
    labels = sorted(weekly_sales.keys())
    data = [weekly_sales[week] for week in labels]
    
    return {
        "labels": labels,
        "data": data,
        "weeks": weeks
    }

# GET: PO forecast vs actual bar chart
@router.get("/charts/po-forecast-vs-actual")
def get_po_forecast_vs_actual(
    weeks: int = Query(12, description="Number of weeks to show"),
    db: Session = Depends(get_db)
):
    """Get PO forecast vs actual comparison data"""
    end_date = date.today()
    start_date = end_date - timedelta(weeks=weeks)
    
    pos = db.query(PurchaseOrder).filter(
        PurchaseOrder.order_week >= start_date,
        PurchaseOrder.order_week <= end_date
    ).order_by(PurchaseOrder.order_week).all()
    
    # Group by week
    weekly_data = {}
    for po in pos:
        week_key = po.order_week.isoformat()
        if week_key not in weekly_data:
            weekly_data[week_key] = {"forecasted": 0, "actual": 0}
        
        forecasted_qty = po.forecasted_quantity if po.forecasted_quantity is not None else po.quantity  # type: ignore
        weekly_data[week_key]["forecasted"] += forecasted_qty
        weekly_data[week_key]["actual"] += po.quantity  # type: ignore
    
    labels = sorted(weekly_data.keys())
    forecasted_data = [weekly_data[week]["forecasted"] for week in labels]
    actual_data = [weekly_data[week]["actual"] for week in labels]
    
    return {
        "labels": labels,
        "forecasted": forecasted_data,
        "actual": actual_data
    }

# GET: Shipment stage distribution donut chart
@router.get("/charts/shipment-stages")
def get_shipment_stages_chart(db: Session = Depends(get_db)):
    """Get shipment stage distribution for donut chart"""
    stages = ["CKD Prepared", "Booking", "Shipped", "Customs", "Assembly"]
    
    stage_counts = {}
    for stage in stages:
        count = db.query(PurchaseOrder).filter(
            PurchaseOrder.stage == stage,
            PurchaseOrder.status.in_(["ordered", "shipped"])
        ).count()
        stage_counts[stage] = count
    
    return {
        "labels": stages,
        "data": [stage_counts[stage] for stage in stages],
        "colors": ["#2196f3", "#ff9800", "#4caf50", "#9c27b0", "#f44336"]
    }

# GET: Lead time performance histogram
@router.get("/charts/lead-time-performance")
def get_lead_time_performance(db: Session = Depends(get_db)):
    """Get lead time performance histogram (actual vs expected)"""
    # Get delivered POs with both order_date and eta
    delivered_pos = db.query(PurchaseOrder).filter(
        PurchaseOrder.status == "delivered",
        PurchaseOrder.order_date.isnot(None),
        PurchaseOrder.eta.isnot(None)
    ).all()
    
    lead_times = []
    for po in delivered_pos:
        if po.order_date and po.eta:  # type: ignore
            actual_lead_time = (po.eta - po.order_date).days  # type: ignore
            lead_times.append(actual_lead_time)
    
    # Create histogram bins (0-30, 31-60, 61-90, 91-120, 120+)
    bins = [0, 30, 60, 90, 120, float('inf')]
    bin_labels = ["0-30", "31-60", "61-90", "91-120", "120+"]
    histogram = [0] * len(bin_labels)
    
    for lead_time in lead_times:
        for i, bin_max in enumerate(bins):
            if lead_time <= bin_max:
                histogram[i] += 1
                break
    
    return {
        "labels": bin_labels,
        "data": histogram,
        "average_lead_time": sum(lead_times) / len(lead_times) if lead_times else 0,
        "total_deliveries": len(lead_times)
    }

