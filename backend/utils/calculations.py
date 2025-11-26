from datetime import date, timedelta
from typing import Dict, List, Tuple
import statistics

# SQLAlchemy import - installed in venv, linter warning is IDE configuration issue
from sqlalchemy.orm import Session  

from models import Inventory, ProductModel, SalesRecord, PurchaseOrder, MonthlyPlan, SalesForecast
from config import settings

class BusinessCalculations:
    """Business calculations for PSI metrics - Based on Excel Sheet 2 formulas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_monthly_psi(self, product_id: int, target_month: date) -> Dict:
        """
        Calculate monthly PSI (Purchase, Sales, Inventory) metrics
        Based on Excel Sheet 2: "PSI" - Main Dashboard
        
        Formulas:
        - Available Sales Inventory = SUM(Weekly Purchases) + Previous Month Ending Inventory
        - Ending Inventory = Available Sales Inventory - Monthly Sales Forecast
        - DOS Days = (Ending Inventory / Monthly Sales Forecast) * 30
        """
        product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            return {}
        
        # Get month start and end
        month_start = target_month.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        month_end = month_end - timedelta(days=1)
        
        # Get opening balance (Previous Month Ending Inventory)
        opening_balance = self.get_opening_balance(product_id, month_start)
        
        # Get weekly purchases breakdown (W1-W4)
        weekly_purchases = self.get_weekly_purchases_breakdown(product_id, month_start, month_end)
        total_weekly_purchases = sum(weekly_purchases.values())
        
        # Calculate Available Sales Inventory (可销售库存)
        # Formula: SUM(Weekly Purchases) + Previous Month Ending Inventory
        available_sales_inventory = total_weekly_purchases + opening_balance
        
        # Get monthly sales forecast (当月销售预测)
        monthly_sales_forecast = self.get_monthly_sales_forecast(product_id, month_start)
        
        # Calculate Ending Inventory (截止库存)
        # Formula: Available Sales Inventory - Monthly Sales Forecast
        ending_inventory = available_sales_inventory - monthly_sales_forecast
        
        # Calculate DOS Days (DOS天数)
        # Formula: (Ending Inventory / Monthly Sales Forecast) * 30
        dos_days = self.calculate_dos_from_forecast(ending_inventory, monthly_sales_forecast)
        
        # Get actual sales for comparison
        monthly_actual_sales = self.get_monthly_sales(product_id, month_start, month_end)
        
        # Get safety_stock_days as int (SQLAlchemy returns actual value from instance at runtime)
        # Type checker sees Column[int] but runtime value is int
        target_dos: int = product.safety_stock_days if product.safety_stock_days is not None else 45  # type: ignore
        
        # Handle None dos_days (when no sales forecast) - convert to None for JSON
        dos_days_value = None if dos_days is None else round(dos_days, 1)
        
        return {
            "product_id": product_id,
            "product_name": str(product.name),  # type: ignore
            "product_sku": str(product.sku),  # type: ignore
            "month": month_start.strftime("%Y-%m"),
            "opening_balance": opening_balance,
            "week_1_purchase": weekly_purchases.get('W1', 0),
            "week_2_purchase": weekly_purchases.get('W2', 0),
            "week_3_purchase": weekly_purchases.get('W3', 0),
            "week_4_purchase": weekly_purchases.get('W4', 0),
            "total_weekly_purchases": total_weekly_purchases,
            "available_sales_inventory": available_sales_inventory,
            "sales_forecast": monthly_sales_forecast,
            "actual_sales": monthly_actual_sales,
            "ending_inventory": ending_inventory,
            "dos_days": dos_days_value,  # None if no sales forecast, otherwise rounded float
            "target_dos": target_dos,
            "status": self.get_dos_status(dos_days, target_dos)
        }
    
    def get_opening_balance(self, product_id: int, month_start: date) -> int:
        """
        Get opening balance for the month (Previous Month Ending Inventory)
        This is the ending inventory from the previous month
        """
        # Calculate previous month
        if month_start.month == 1:
            prev_month = month_start.replace(year=month_start.year - 1, month=12)
        else:
            prev_month = month_start.replace(month=month_start.month - 1)
        
        # Try to get from MonthlyPlan first (most accurate)
        monthly_plan = self.db.query(MonthlyPlan).filter(
            MonthlyPlan.product_id == product_id,
            MonthlyPlan.plan_month == prev_month
        ).order_by(MonthlyPlan.version.desc()).first()
        
        if monthly_plan and monthly_plan.ending_inventory is not None:
            return monthly_plan.ending_inventory  # type: ignore
        
        # Fallback to current inventory if no plan exists
        inventory = self.db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if inventory:
            return inventory.current_stock if inventory.current_stock is not None else 0  # type: ignore
        return 0
    
    def get_weekly_purchases_breakdown(self, product_id: int, month_start: date, month_end: date) -> Dict[str, int]:
        """
        Get weekly purchases breakdown (W1-W4) for the month
        Based on Excel Sheet 2: Weekly breakdown for each month
        """
        # Get all purchases for the month
        purchases = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.product_id == product_id,
            PurchaseOrder.order_week >= month_start,
            PurchaseOrder.order_week <= month_end,
            PurchaseOrder.status.in_(["ordered", "shipped", "delivered"])
        ).order_by(PurchaseOrder.order_week).all()
        
        # Calculate week boundaries
        week_1_end = month_start + timedelta(days=6)
        week_2_end = month_start + timedelta(days=13)
        week_3_end = month_start + timedelta(days=20)
        week_4_end = month_end
        
        weekly_purchases = {'W1': 0, 'W2': 0, 'W3': 0, 'W4': 0}
        
        for po in purchases:
            po_date = po.order_week
            po_quantity: int = po.quantity if po.quantity is not None else 0  # type: ignore
            # Date comparisons work correctly at runtime despite type checker warnings
            if po_date <= week_1_end:  # type: ignore[operator]
                weekly_purchases['W1'] += po_quantity  # type: ignore[assignment]
            elif po_date <= week_2_end:  # type: ignore[operator]
                weekly_purchases['W2'] += po_quantity  # type: ignore[assignment]
            elif po_date <= week_3_end:  # type: ignore[operator]
                weekly_purchases['W3'] += po_quantity  # type: ignore[assignment]
            else:
                weekly_purchases['W4'] += po_quantity  # type: ignore[assignment]
        
        return weekly_purchases
    
    def get_monthly_purchases(self, product_id: int, month_start: date, month_end: date) -> int:
        """Get total purchases for the month (sum of all weekly purchases)"""
        weekly_purchases = self.get_weekly_purchases_breakdown(product_id, month_start, month_end)
        return sum(weekly_purchases.values())
    
    def get_monthly_sales(self, product_id: int, month_start: date, month_end: date) -> int:
        """Get total sales for the month"""
        sales = self.db.query(SalesRecord).filter(
            SalesRecord.product_id == product_id,
            SalesRecord.sale_date >= month_start,
            SalesRecord.sale_date <= month_end
        ).all()
        
        return sum(sale.quantity if sale.quantity is not None else 0 for sale in sales)  # type: ignore
    
    def get_monthly_sales_forecast(self, product_id: int, month_start: date) -> int:
        """
        Get monthly sales forecast (当月销售预测)
        Priority: Use actual sales data if available, otherwise use SalesForecast table
        Based on Excel Sheet 4: Sales forecast data
        """
        # First, try to get actual sales for the month (if month has passed or is current)
        from datetime import date as date_type
        month_end = month_start
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        month_end = month_end - timedelta(days=1)
        
        # If month is in the past or current, use actual sales
        if month_end <= date_type.today():
            actual_sales = self.get_monthly_sales(product_id, month_start, month_end)
            if actual_sales > 0:
                return actual_sales
        
        # Otherwise, get forecast from SalesForecast table
        forecast = self.db.query(SalesForecast).filter(
            SalesForecast.product_id == product_id,
            SalesForecast.forecast_date == month_start,
            SalesForecast.channel == "all"  # All-channel forecast
        ).order_by(SalesForecast.version.desc()).first()
        
        if forecast:
            return forecast.quantity if forecast.quantity is not None else 0  # type: ignore
        
        # If no forecast exists, calculate from historical sales trend
        # Use last 3 months average as fallback
        from datetime import date as date_type
        end_date = month_start - timedelta(days=1)
        start_date = end_date - timedelta(days=90)  # 3 months back
        
        historical_sales = self.get_monthly_sales(product_id, start_date, end_date)
        # Approximate monthly average
        return int(historical_sales / 3) if historical_sales > 0 else 0
    
    def calculate_dos_from_forecast(self, ending_inventory: int, monthly_sales_forecast: int) -> float | None:
        """
        Calculate DOS Days (DOS天数) based on Excel Sheet 2 formula
        Formula: (Ending Inventory / Monthly Sales Forecast) * 30
        Returns None if no sales forecast (instead of inf for JSON compatibility)
        """
        if monthly_sales_forecast <= 0:
            return None  # Use None instead of inf for JSON compatibility
        return (ending_inventory / monthly_sales_forecast) * 30
    
    def calculate_dos(self, ending_inventory: int, monthly_sales: int) -> float | None:
        """
        Calculate Days of Supply from actual sales
        Alternative method using actual sales data
        Returns None if no sales (instead of inf for JSON compatibility)
        """
        if monthly_sales <= 0:
            return None  # Use None instead of inf for JSON compatibility
        daily_sales = monthly_sales / 30  # Approximate daily sales
        if daily_sales <= 0:
            return None  # Use None instead of inf for JSON compatibility
        return ending_inventory / daily_sales
    
    def get_dos_status(self, dos_days: float | None, target_dos: int) -> str:
        """Determine DOS status based on target ranges"""
        if dos_days is None:
            return "No Sales"
        
        # Check if it's a new branch (target 50-60) or established (<45)
        if target_dos >= 50:
            # New branch: 50-60 days is healthy
            if 50 <= dos_days <= 60:
                return "Healthy"
            elif dos_days < 50:
                return "Low Stock"
            else:
                return "Overstock"
        else:
            # Established branch: <45 days is healthy
            if dos_days <= 45:
                return "Healthy"
            else:
                return "Overstock"
    
    def calculate_n_plus_3_stock(self, product_id: int) -> Dict:
        """
        Calculate N+3 rolling stock projection
        Based on Excel Sheet 3: "N+3 rolling stock"
        
        End-to-End Inventory Formula:
        End-to-End Inventory = Branch finished goods + Factory kits + Sea shipping + Domestic ODF
        """
        product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            return {}
        
        # Get current inventory components
        inventory = self.db.query(Inventory).filter(Inventory.product_id == product_id).first()
        
        # Branch finished goods (CBU in hand - Complete Built Units in warehouse)
        cbu_in_hand: int = inventory.cbu_in_hand if inventory and inventory.cbu_in_hand is not None else 0  # type: ignore
        
        # Factory kits (CKD kits being assembled)
        kits_in_factory: int = inventory.kits_in_factory if inventory and inventory.kits_in_factory is not None else 0  # type: ignore
        
        # Sea shipping (In-transit inventory based on ETA)
        three_months_later = date.today() + timedelta(days=90)
        sea_shipping = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.product_id == product_id,
            PurchaseOrder.eta <= three_months_later,
            PurchaseOrder.eta > date.today(),
            PurchaseOrder.status.in_(["ordered", "shipped"]),
            PurchaseOrder.stage.in_(["shipped", "customs", None])  # In transit
        ).all()
        sea_shipping_qty = sum(po.quantity if po.quantity is not None else 0 for po in sea_shipping)  # type: ignore
        
        # Domestic ODF (Order Fulfillment) - Purchase orders that are ordered but not yet in transit
        domestic_odf = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.product_id == product_id,
            PurchaseOrder.eta <= three_months_later,
            PurchaseOrder.status == "ordered",
            PurchaseOrder.stage.in_(["CKD materials", "booking", None])
        ).all()
        domestic_odf_qty = sum(po.quantity if po.quantity is not None else 0 for po in domestic_odf)  # type: ignore
        
        # Calculate End-to-End Inventory (端到端库存)
        # Formula: Branch finished goods + Factory kits + Sea shipping + Domestic ODF
        end_to_end_inventory = cbu_in_hand + kits_in_factory + sea_shipping_qty + domestic_odf_qty
        
        # N+3 Stock = End-to-End Inventory
        n_plus_3_stock = end_to_end_inventory
        
        return {
            "product_id": product_id,
            "product_name": str(product.name),  # type: ignore
            "product_sku": str(product.sku),  # type: ignore
            "cbu_in_hand": cbu_in_hand,  # Branch finished goods
            "kits_in_factory": kits_in_factory,  # Factory kits
            "sea_shipping": sea_shipping_qty,  # In-transit (sea shipping)
            "domestic_odf": domestic_odf_qty,  # Domestic Order Fulfillment
            "end_to_end_inventory": end_to_end_inventory,  # Total end-to-end inventory
            "n_plus_3_stock": n_plus_3_stock,  # N+3 rolling stock
            "projection_date": three_months_later.strftime("%Y-%m-%d"),
            "breakdown": {
                "branch_finished_goods": cbu_in_hand,
                "factory_kits": kits_in_factory,
                "sea_shipping": sea_shipping_qty,
                "domestic_odf": domestic_odf_qty
            }
        }

def get_calculations_engine(db: Session) -> BusinessCalculations:
    """Dependency injection for calculations engine"""
    return BusinessCalculations(db)