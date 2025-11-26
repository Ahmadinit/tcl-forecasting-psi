from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from database import get_db
from models import MonthlyPlan, ProductModel
from utils.calculations import BusinessCalculations

router = APIRouter(
    prefix="/monthly-plan",
    tags=["monthly-plan"]
)

class MonthlyPlanCreate(BaseModel):
    product_id: int
    plan_month: date
    week_1_purchase: int = 0
    week_2_purchase: int = 0
    week_3_purchase: int = 0
    week_4_purchase: int = 0
    sales_forecast: int = 0
    version: str = "v1.0"

class MonthlyPlanUpdate(BaseModel):
    week_1_purchase: Optional[int] = None
    week_2_purchase: Optional[int] = None
    week_3_purchase: Optional[int] = None
    week_4_purchase: Optional[int] = None
    sales_forecast: Optional[int] = None
    version: Optional[str] = None

class MessageResponse(BaseModel):
    message: str

# GET: List all monthly plans
@router.get("")
def list_monthly_plans(
    product_id: Optional[int] = None,
    plan_month: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get all monthly plans with filtering"""
    query = db.query(MonthlyPlan, ProductModel).join(
        ProductModel, MonthlyPlan.product_id == ProductModel.id
    ).filter(ProductModel.is_active == True)
    
    if product_id:
        query = query.filter(MonthlyPlan.product_id == product_id)
    if plan_month:
        # Normalize to first day of month
        month_start = plan_month.replace(day=1)
        query = query.filter(MonthlyPlan.plan_month == month_start)
    
    plans = query.order_by(MonthlyPlan.plan_month.desc(), MonthlyPlan.product_id).all()
    
    return [
        {
            "id": plan.id,
            "product_id": plan.product_id,
            "product_name": product.name,
            "product_sku": product.sku,
            "plan_month": plan.plan_month.isoformat(),
            "week_1_purchase": plan.week_1_purchase,
            "week_2_purchase": plan.week_2_purchase,
            "week_3_purchase": plan.week_3_purchase,
            "week_4_purchase": plan.week_4_purchase,
            "opening_balance": plan.opening_balance,
            "sales_forecast": plan.sales_forecast,
            "ending_inventory": plan.ending_inventory,
            "dos_days": plan.dos_days,
            "version": plan.version,
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "updated_at": plan.updated_at.isoformat() if plan.updated_at else None
        }
        for plan, product in plans
    ]

# POST: Create or update monthly plan with auto-calculation
@router.post("/create")
def create_monthly_plan(payload: MonthlyPlanCreate, db: Session = Depends(get_db)):
    """
    Create a monthly plan with automatic PSI calculation
    Based on Excel Sheet 2 business logic
    """
    # Check if product exists
    product = db.query(ProductModel).filter(
        ProductModel.id == payload.product_id,
        ProductModel.is_active == True
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Normalize plan_month to first day of month
    month_start = payload.plan_month.replace(day=1)
    
    # Check if plan already exists
    existing_plan = db.query(MonthlyPlan).filter(
        MonthlyPlan.product_id == payload.product_id,
        MonthlyPlan.plan_month == month_start,
        MonthlyPlan.version == payload.version
    ).first()
    
    if existing_plan:
        raise HTTPException(
            status_code=400,
            detail=f"Monthly plan already exists for {month_start.strftime('%Y-%m')} version {payload.version}"
        )
    
    # Use BusinessCalculations to calculate PSI metrics
    calculations = BusinessCalculations(db)
    
    # Get opening balance (previous month ending inventory)
    opening_balance = calculations.get_opening_balance(payload.product_id, month_start)
    
    # Calculate total weekly purchases
    total_weekly_purchases = (
        payload.week_1_purchase +
        payload.week_2_purchase +
        payload.week_3_purchase +
        payload.week_4_purchase
    )
    
    # Calculate available sales inventory
    # Formula: SUM(Weekly Purchases) + Previous Month Ending Inventory
    available_sales_inventory = total_weekly_purchases + opening_balance
    
    # Calculate ending inventory
    # Formula: Available Sales Inventory - Monthly Sales Forecast
    ending_inventory = available_sales_inventory - payload.sales_forecast
    
    # Calculate DOS days
    # Formula: (Ending Inventory / Monthly Sales Forecast) * 30
    dos_days = calculations.calculate_dos_from_forecast(ending_inventory, payload.sales_forecast)
    
    # Create monthly plan
    monthly_plan = MonthlyPlan(
        product_id=payload.product_id,
        plan_month=month_start,
        week_1_purchase=payload.week_1_purchase,
        week_2_purchase=payload.week_2_purchase,
        week_3_purchase=payload.week_3_purchase,
        week_4_purchase=payload.week_4_purchase,
        opening_balance=opening_balance,
        sales_forecast=payload.sales_forecast,
        ending_inventory=ending_inventory,
        dos_days=dos_days,
        version=payload.version
    )
    
    db.add(monthly_plan)
    db.commit()
    db.refresh(monthly_plan)
    
    return {
        "id": monthly_plan.id,
        "product_id": monthly_plan.product_id,
        "product_name": product.name,
        "product_sku": product.sku,
        "plan_month": monthly_plan.plan_month.isoformat(),
        "week_1_purchase": monthly_plan.week_1_purchase,
        "week_2_purchase": monthly_plan.week_2_purchase,
        "week_3_purchase": monthly_plan.week_3_purchase,
        "week_4_purchase": monthly_plan.week_4_purchase,
        "opening_balance": monthly_plan.opening_balance,
        "available_sales_inventory": available_sales_inventory,
        "sales_forecast": monthly_plan.sales_forecast,
        "ending_inventory": monthly_plan.ending_inventory,
        "dos_days": round(monthly_plan.dos_days, 1),  # type: ignore
        "version": monthly_plan.version
    }

# GET: Get monthly plan by ID
@router.get("/{plan_id}")
def get_monthly_plan(plan_id: int, db: Session = Depends(get_db)):
    """Get a specific monthly plan"""
    plan = db.query(MonthlyPlan, ProductModel).join(
        ProductModel, MonthlyPlan.product_id == ProductModel.id
    ).filter(MonthlyPlan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Monthly plan not found")
    
    monthly_plan, product = plan
    
    return {
        "id": monthly_plan.id,
        "product_id": monthly_plan.product_id,
        "product_name": product.name,
        "product_sku": product.sku,
        "plan_month": monthly_plan.plan_month.isoformat(),
        "week_1_purchase": monthly_plan.week_1_purchase,
        "week_2_purchase": monthly_plan.week_2_purchase,
        "week_3_purchase": monthly_plan.week_3_purchase,
        "week_4_purchase": monthly_plan.week_4_purchase,
        "opening_balance": monthly_plan.opening_balance,
        "sales_forecast": monthly_plan.sales_forecast,
        "ending_inventory": monthly_plan.ending_inventory,
        "dos_days": round(monthly_plan.dos_days, 1),  # type: ignore
        "version": monthly_plan.version,
        "created_at": monthly_plan.created_at.isoformat() if monthly_plan.created_at else None,
        "updated_at": monthly_plan.updated_at.isoformat() if monthly_plan.updated_at else None
    }

# PUT: Update monthly plan with auto-recalculation
@router.put("/{plan_id}")
def update_monthly_plan(plan_id: int, payload: MonthlyPlanUpdate, db: Session = Depends(get_db)):
    """Update monthly plan and recalculate PSI metrics"""
    plan = db.query(MonthlyPlan).filter(MonthlyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Monthly plan not found")
    
    # Update fields if provided
    if payload.week_1_purchase is not None:
        plan.week_1_purchase = payload.week_1_purchase  # type: ignore
    if payload.week_2_purchase is not None:
        plan.week_2_purchase = payload.week_2_purchase  # type: ignore
    if payload.week_3_purchase is not None:
        plan.week_3_purchase = payload.week_3_purchase  # type: ignore
    if payload.week_4_purchase is not None:
        plan.week_4_purchase = payload.week_4_purchase  # type: ignore
    if payload.sales_forecast is not None:
        plan.sales_forecast = payload.sales_forecast  # type: ignore
    if payload.version is not None:
        plan.version = payload.version  # type: ignore
    
    # Recalculate PSI metrics
    calculations = BusinessCalculations(db)
    
    total_weekly_purchases = (
        plan.week_1_purchase +  # type: ignore
        plan.week_2_purchase +  # type: ignore
        plan.week_3_purchase +  # type: ignore
        plan.week_4_purchase  # type: ignore
    )
    
    available_sales_inventory = total_weekly_purchases + plan.opening_balance  # type: ignore
    plan.ending_inventory = available_sales_inventory - plan.sales_forecast  # type: ignore
    plan.dos_days = calculations.calculate_dos_from_forecast(plan.ending_inventory, plan.sales_forecast)  # type: ignore
    
    db.commit()
    db.refresh(plan)
    
    product = db.query(ProductModel).filter(ProductModel.id == plan.product_id).first()
    
    return {
        "id": plan.id,
        "product_id": plan.product_id,
        "product_name": product.name if product else "Unknown",
        "plan_month": plan.plan_month.isoformat(),
        "week_1_purchase": plan.week_1_purchase,
        "week_2_purchase": plan.week_2_purchase,
        "week_3_purchase": plan.week_3_purchase,
        "week_4_purchase": plan.week_4_purchase,
        "opening_balance": plan.opening_balance,
        "available_sales_inventory": available_sales_inventory,
        "sales_forecast": plan.sales_forecast,
        "ending_inventory": plan.ending_inventory,
        "dos_days": round(plan.dos_days, 1),  # type: ignore
        "version": plan.version
    }

# POST: Auto-generate monthly plan from calculations
@router.post("/auto-generate")
def auto_generate_monthly_plan(
    product_id: int = Query(..., description="Product ID"),
    plan_month: date = Query(..., description="Target month (YYYY-MM-DD)"),
    version: str = Query("v1.0", description="Plan version"),
    db: Session = Depends(get_db)
):
    """
    Auto-generate monthly plan using PSI calculations
    Pulls data from PurchaseOrders and SalesForecasts
    """
    # Check if product exists
    product = db.query(ProductModel).filter(
        ProductModel.id == product_id,
        ProductModel.is_active == True
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Normalize plan_month
    month_start = plan_month.replace(day=1)
    
    # Use BusinessCalculations to get all data
    calculations = BusinessCalculations(db)
    psi_data = calculations.calculate_monthly_psi(product_id, month_start)
    
    if not psi_data:
        raise HTTPException(status_code=400, detail="Could not calculate PSI data")
    
    # Check if plan already exists
    existing_plan = db.query(MonthlyPlan).filter(
        MonthlyPlan.product_id == product_id,
        MonthlyPlan.plan_month == month_start,
        MonthlyPlan.version == version
    ).first()
    
    if existing_plan:
        # Update existing plan
        existing_plan.week_1_purchase = psi_data.get('week_1_purchase', 0)
        existing_plan.week_2_purchase = psi_data.get('week_2_purchase', 0)
        existing_plan.week_3_purchase = psi_data.get('week_3_purchase', 0)
        existing_plan.week_4_purchase = psi_data.get('week_4_purchase', 0)
        existing_plan.opening_balance = psi_data.get('opening_balance', 0)
        existing_plan.sales_forecast = psi_data.get('sales_forecast', 0)
        existing_plan.ending_inventory = psi_data.get('ending_inventory', 0)
        existing_plan.dos_days = psi_data.get('dos_days', 0)
        existing_plan.version = version  # type: ignore
        
        db.commit()
        db.refresh(existing_plan)
        plan = existing_plan
    else:
        # Create new plan
        plan = MonthlyPlan(
            product_id=product_id,
            plan_month=month_start,
            week_1_purchase=psi_data.get('week_1_purchase', 0),
            week_2_purchase=psi_data.get('week_2_purchase', 0),
            week_3_purchase=psi_data.get('week_3_purchase', 0),
            week_4_purchase=psi_data.get('week_4_purchase', 0),
            opening_balance=psi_data.get('opening_balance', 0),
            sales_forecast=psi_data.get('sales_forecast', 0),
            ending_inventory=psi_data.get('ending_inventory', 0),
            dos_days=psi_data.get('dos_days', 0),
            version=version
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
    
    return {
        "id": plan.id,
        "product_id": plan.product_id,
        "product_name": product.name,
        "plan_month": plan.plan_month.isoformat(),
        **psi_data
    }

# DELETE: Delete monthly plan
@router.delete("/{plan_id}")
def delete_monthly_plan(plan_id: int, db: Session = Depends(get_db)):
    """Delete a monthly plan"""
    plan = db.query(MonthlyPlan).filter(MonthlyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Monthly plan not found")
    
    db.delete(plan)
    db.commit()
    return {"message": "Monthly plan deleted successfully"}

