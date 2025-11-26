import numpy as np  
from datetime import date, timedelta
from sqlalchemy.orm import Session  
from models import SalesRecord, ProductModel, Inventory, SalesForecast
from typing import List, Dict, Tuple
import statistics
from config import settings

class ForecastEngine:
    """
    Purchase Forecasting Engine - Forecasts PURCHASES based on SALES DATA and INVENTORY
    Flow: Actual Sales Data → Predict Future Demand → Calculate Required Purchases
    
    Based on Excel business logic:
    - Uses weighted moving average of actual sales records
    - Considers current inventory levels
    - Calculates safety stock based on demand variability
    - Generates purchase quantity suggestions
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_weighted_moving_average(self, sales_data: List, weights: List[float] | None = None) -> float:
        """
        Calculate weighted moving average for sales forecasting
        Based on Excel business logic: Uses weights from config [0.5, 0.3, 0.15, 0.05] for recent weeks
        """
        if weights is None:
            weights = settings.FORECAST_WEIGHTS  # Use weights from config
        
        if not sales_data:
            return 0
        
        # Use only the most recent data points based on weights length
        recent_data = sales_data[-len(weights):]
        
        # Pad with zeros if we don't have enough data
        while len(recent_data) < len(weights):
            recent_data.insert(0, 0)
        
        # Calculate weighted average
        weighted_sum = sum(data * weight for data, weight in zip(recent_data, weights))
        return weighted_sum
    
    def get_weekly_sales_data(self, product_id: int, weeks: int = 8, channel: str = "all") -> List[float]:
        """
        Get weekly sales data for a product
        Based on Excel Sheet 4: Multi-channel sales data
        
        Args:
            product_id: Product ID
            weeks: Number of weeks of historical data
            channel: Sales channel ("ecommerce", "A101", "wholesale", "all")
        """
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks)
        
        # Get sales data grouped by week
        query = self.db.query(SalesRecord).filter(
            SalesRecord.product_id == product_id,
            SalesRecord.sale_date >= start_date,
            SalesRecord.sale_date <= end_date
        )
        
        # Filter by channel if specified
        if channel != "all":
            query = query.filter(SalesRecord.channel == channel)
        
        sales_data = query.order_by(SalesRecord.sale_date).all()
        
        # Group by week (using ISO week)
        weekly_sales = {}
        for sale in sales_data:
            year, week_num, _ = sale.sale_date.isocalendar()
            week_key = f"{year}-W{week_num:02d}"
            if week_key not in weekly_sales:
                weekly_sales[week_key] = 0
            weekly_sales[week_key] += sale.quantity
        
        # Return sorted list of weekly sales values
        sorted_weeks = sorted(weekly_sales.keys())
        return [weekly_sales[week] for week in sorted_weeks]
    
    def aggregate_multi_channel_sales(self, product_id: int, target_month: date) -> Dict:
        """
        Aggregate multi-channel sales forecast
        Based on Excel Sheet 4: All-Channel Sales Forecast (全渠道销售预测)
        
        Channels: E-commerce + A101 + Traditional wholesale
        """
        month_start = target_month.replace(day=1)
        
        # Get forecasts for each channel
        channels = ["ecommerce", "A101", "wholesale"]
        channel_forecasts = {}
        total_forecast = 0
        
        for channel in channels:
            forecast = self.db.query(SalesForecast).filter(
                SalesForecast.product_id == product_id,
                SalesForecast.forecast_date == month_start,
                SalesForecast.channel == channel
            ).order_by(SalesForecast.version.desc()).first()
            
            qty = forecast.quantity if forecast else 0
            channel_forecasts[channel] = qty
            total_forecast += qty
        
        # Get all-channel forecast if exists
        all_channel_forecast = self.db.query(SalesForecast).filter(
            SalesForecast.product_id == product_id,
            SalesForecast.forecast_date == month_start,
            SalesForecast.channel == "all"
        ).order_by(SalesForecast.version.desc()).first()
        
        return {
            "product_id": product_id,
            "month": month_start.strftime("%Y-%m"),
            "ecommerce": channel_forecasts.get("ecommerce", 0),
            "A101": channel_forecasts.get("A101", 0),
            "wholesale": channel_forecasts.get("wholesale", 0),
            "total_all_channels": total_forecast,
            "all_channel_forecast": all_channel_forecast.quantity if all_channel_forecast else total_forecast
        }
    
    def calculate_safety_stock(self, product_id: int, service_level: float = 0.95) -> float:
        """Calculate safety stock based on demand variability and lead time"""
        sales_data = self.get_weekly_sales_data(product_id, 12)  # 12 weeks of data
        
        if len(sales_data) < 4:
            return 0
        
        # Calculate standard deviation of demand
        demand_std = statistics.stdev(sales_data) if len(sales_data) > 1 else 0
        
        # Get lead time from system config
        lead_time_weeks = settings.LEAD_TIME_DAYS / 7
        
        # Safety stock formula: Z * σ * √(Lead Time)
        # Z-score for service level (95% = 1.65, 99% = 2.33)
        z_score = 1.65 if settings.SERVICE_LEVEL == 0.95 else 2.33
        safety_stock = z_score * demand_std * (lead_time_weeks ** 0.5)
        
        return max(0, safety_stock)
    
    def generate_purchase_forecast(self, product_id: int, forecast_weeks: int = 4) -> Dict:
        """Generate purchase forecast based on sales trends"""
        product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            return {}
        
        inventory = self.db.query(Inventory).filter(Inventory.product_id == product_id).first()
        current_stock = inventory.current_stock if inventory else 0
        
        # Get sales data
        sales_data = self.get_weekly_sales_data(product_id)
        
        # Calculate forecasted demand
        if sales_data:
            forecasted_demand = self.calculate_weighted_moving_average(sales_data)
        else:
            # No sales data, use safety stock approach
            forecasted_demand = product.safety_stock_days / 7  # Convert days to weekly
        
        # Calculate required inventory for forecast period
        required_inventory = (forecasted_demand * forecast_weeks) + self.calculate_safety_stock(product_id)
        
        # Calculate suggested purchase quantity
        # Convert to float for calculations (SQLAlchemy returns actual values at runtime)
        current_stock_float = float(current_stock) if current_stock is not None else 0.0  # type: ignore
        required_inventory_float = float(required_inventory)  # type: ignore
        suggested_quantity = max(0.0, required_inventory_float - current_stock_float)
        
        safety_stock_val = self.calculate_safety_stock(product_id)
        safety_stock_float: float = float(safety_stock_val) if safety_stock_val is not None else 0.0  # type: ignore
        
        # Convert forecasted_demand to float (SQLAlchemy returns actual value at runtime)
        forecasted_demand_float: float = float(forecasted_demand)  # type: ignore
        
        return {
            "product_id": product_id,
            "product_name": str(product.name),  # type: ignore
            "current_stock": int(current_stock_float),
            "forecasted_weekly_demand": round(forecasted_demand_float, 2),
            "safety_stock": round(safety_stock_float),
            "required_inventory": round(required_inventory_float),
            "suggested_purchase_quantity": round(suggested_quantity),
            "confidence_level": "High" if len(sales_data) >= 4 else "Low",
            "data_points_used": len(sales_data)
        }
    
    def calculate_dos(self, current_stock: int, forecasted_demand: float) -> float:
        """Calculate Days of Supply (DOS)"""
        if forecasted_demand <= 0:
            return float('inf')
        return (current_stock / forecasted_demand) * 7  # Convert weeks to days

def get_forecast_engine(db: Session) -> ForecastEngine:
    """Dependency injection for forecast engine"""
    return ForecastEngine(db)