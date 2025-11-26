"""
Weekly Purchase Order Generator
Generates POs every Saturday (6th day) for all products based on:
PO Quantity = (Weekly Consumption × Lead Time Weeks) + Safety Stock - Current Inventory
"""
from datetime import date, timedelta, datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from models import ProductModel, Inventory, SalesRecord, PurchaseOrder, SystemConfig
from config import settings


class WeeklyPOGenerator:
    """Generate weekly purchase orders automatically"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_system_config(self, key: str, default_value: str) -> str:
        """Get system configuration value"""
        config = self.db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        return config.config_value if config else default_value  # type: ignore
    
    def get_weekly_consumption(self, product_id: int, week_start: date) -> int:
        """
        Calculate weekly consumption (sales) for a given week
        Week is Monday to Friday (5 business days)
        """
        week_end = week_start + timedelta(days=4)  # Friday
        
        sales = self.db.query(SalesRecord).filter(
            and_(
                SalesRecord.product_id == product_id,
                SalesRecord.sale_date >= week_start,
                SalesRecord.sale_date <= week_end
            )
        ).all()
        
        return sum(sale.quantity if sale.quantity is not None else 0 for sale in sales)  # type: ignore
    
    def calculate_safety_stock(self, product_id: int) -> int:
        """
        Calculate safety stock as: Current Inventory × Safety Threshold Percentage
        """
        product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            return 0
        
        inventory = self.db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory or inventory.current_stock is None:
            return 0
        
        current_stock = inventory.current_stock  # type: ignore
        safety_threshold = product.safety_threshold_percentage if product.safety_threshold_percentage is not None else 20.0  # type: ignore
        
        safety_stock = int(current_stock * (safety_threshold / 100.0))  # type: ignore
        return safety_stock
    
    def calculate_po_quantity(
        self, 
        product_id: int, 
        weekly_consumption: int,
        lead_time_weeks: int,
        safety_stock: int,
        current_inventory: int
    ) -> int:
        """
        Calculate PO Quantity using the formula:
        PO Quantity = (Weekly Consumption × Lead Time Weeks) + Safety Stock - Current Inventory
        If negative, return 0
        """
        lead_time_demand = weekly_consumption * lead_time_weeks
        po_quantity = (lead_time_demand + safety_stock) - current_inventory
        
        return max(0, po_quantity)  # Never return negative
    
    def get_previous_week_saturday(self) -> date:
        """Get the Saturday of the previous week (the 6th day after Monday)"""
        today = date.today()
        # Get last Monday
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday)
        # Get Saturday (6th day: Monday + 5 days)
        saturday = last_monday + timedelta(days=5)
        return saturday
    
    def get_current_week_saturday(self) -> date:
        """Get the Saturday of the current week"""
        today = date.today()
        # Get this Monday
        days_since_monday = today.weekday()
        this_monday = today - timedelta(days=days_since_monday)
        # Get Saturday (6th day: Monday + 5 days)
        saturday = this_monday + timedelta(days=5)
        return saturday
    
    def generate_weekly_pos(self, order_week: date | None = None) -> Dict:  # type: ignore
        """
        Generate POs for all active products for a given week
        If order_week is None, uses the current week's Saturday
        """
        if order_week is None:  # type: ignore
            order_week = self.get_current_week_saturday()
        
        # Get previous week's Monday to Friday for consumption calculation
        previous_week_monday = order_week - timedelta(days=6)  # Saturday - 6 days = previous Monday
        
        # Get all active products
        products = self.db.query(ProductModel).filter(ProductModel.is_active == True).all()
        
        generated_pos = []
        skipped = []
        
        for product in products:
            # Check if PO already exists for this week
            existing_po = self.db.query(PurchaseOrder).filter(
                and_(
                    PurchaseOrder.product_id == product.id,
                    PurchaseOrder.order_week == order_week
                )
            ).first()
            
            if existing_po:
                skipped.append({
                    "product_id": product.id,
                    "product_sku": product.sku,
                    "reason": "PO already exists for this week"
                })
                continue
            
            # Get inventory
            inventory = self.db.query(Inventory).filter(Inventory.product_id == product.id).first()
            current_inventory = inventory.current_stock if inventory and inventory.current_stock is not None else 0  # type: ignore
            
            # Get weekly consumption (previous week's sales)
            weekly_consumption = self.get_weekly_consumption(product.id, previous_week_monday)  # type: ignore
            
            # Get lead time (product-specific or system default)
            lead_time_weeks = product.lead_time_weeks if product.lead_time_weeks is not None else 10  # type: ignore
            
            # Calculate safety stock
            safety_stock = self.calculate_safety_stock(product.id)  # type: ignore
            
            # Calculate PO quantity
            po_quantity = self.calculate_po_quantity(
                product.id,  # type: ignore
                weekly_consumption,
                int(lead_time_weeks) if lead_time_weeks is not None else 10,  # type: ignore
                safety_stock,
                int(current_inventory) if current_inventory is not None else 0  # type: ignore
            )
            
            # Calculate expected delivery week
            expected_delivery_week = order_week + timedelta(weeks=lead_time_weeks)  # type: ignore
            
            # Create PO (even if quantity is 0, as per requirements)
            po = PurchaseOrder(
                product_id=product.id,
                quantity=po_quantity,
                forecasted_quantity=po_quantity,
                order_week=order_week,
                order_date=order_week,
                expected_delivery_week=expected_delivery_week,
                status='suggested',
                shipping_mode=product.shipping_mode,
                stage='CKD Prepared',
                notes=f"Auto-generated PO. Weekly consumption: {weekly_consumption}, Safety stock: {safety_stock}, Current inventory: {current_inventory}"
            )
            
            self.db.add(po)
            generated_pos.append({
                "product_id": product.id,
                "product_sku": product.sku,
                "quantity": po_quantity,
                "weekly_consumption": weekly_consumption,
                "safety_stock": safety_stock,
                "current_inventory": current_inventory
            })
        
        self.db.commit()
        
        return {
            "order_week": order_week.isoformat(),
            "generated_count": len(generated_pos),
            "skipped_count": len(skipped),
            "purchase_orders": generated_pos,
            "skipped": skipped
        }
    
    def generate_annual_pos(self, year: int | None = None) -> Dict:  # type: ignore
        """
        Generate 52 POs per product for a given year
        One PO per week (every Saturday)
        """
        if year is None:
            year = date.today().year
        
        # Get first Saturday of the year
        jan_1 = date(year, 1, 1)
        days_to_saturday = (5 - jan_1.weekday()) % 7  # Days until next Saturday
        if days_to_saturday == 0 and jan_1.weekday() != 5:
            days_to_saturday = 7
        first_saturday = jan_1 + timedelta(days=days_to_saturday)
        
        all_results = []
        current_saturday = first_saturday
        
        # Generate 52 weeks of POs
        for week_num in range(52):
            result = self.generate_weekly_pos(current_saturday)
            all_results.append(result)
            current_saturday += timedelta(weeks=1)
        
        return {
            "year": year,
            "total_weeks": 52,
            "results": all_results
        }

