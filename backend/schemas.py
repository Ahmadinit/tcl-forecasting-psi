from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import date, datetime

# Base schemas
class ProductBase(BaseModel):
    sku: str
    name: str
    shipping_mode: str
    status: str
    remarks: Optional[str] = None
    safety_stock_days: int = 45
    safety_threshold_percentage: float = 20.0  # Safety stock as % of current inventory
    lead_time_weeks: int = 10  # Lead time in weeks

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Inventory schemas
class InventoryBase(BaseModel):
    product_id: int
    current_stock: int = 0
    cbu_in_hand: int = 0
    kits_in_factory: int = 0

class InventoryCreate(InventoryBase):
    pass

class Inventory(InventoryBase):
    id: int
    last_updated: datetime
    product: Optional[Product] = None
    
    class Config:
        from_attributes = True

# Sales schemas
class SalesRecordBase(BaseModel):
    product_id: int
    sale_date: date
    quantity: int
    channel: str

class SalesRecordCreate(SalesRecordBase):
    pass

class SalesRecord(SalesRecordBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Forecast schemas
class SalesForecastBase(BaseModel):
    product_id: int
    forecast_date: date
    channel: str
    quantity: int
    forecast_type: str
    version: str

class SalesForecastCreate(SalesForecastBase):
    pass

class SalesForecast(SalesForecastBase):
    id: int
    created_at: datetime
    product: Optional[Product] = None
    
    class Config:
        from_attributes = True

# Purchase Order schemas
class PurchaseOrderBase(BaseModel):
    product_id: int
    quantity: int
    forecasted_quantity: Optional[int] = None
    order_week: date
    order_date: Optional[date] = None
    expected_delivery_week: Optional[date] = None
    etd: Optional[date] = None
    eta: Optional[date] = None
    status: str = 'suggested'
    shipping_mode: str
    stage: Optional[str] = 'CKD Prepared'
    notes: Optional[str] = None

class PurchaseOrderCreate(PurchaseOrderBase):
    pass

class PurchaseOrder(PurchaseOrderBase):
    id: int
    po_number: Optional[str]
    created_at: datetime
    updated_at: datetime
    product: Optional[Product] = None
    
    class Config:
        from_attributes = True

# Monthly Plan schemas
class MonthlyPlanBase(BaseModel):
    product_id: int
    plan_month: date
    week_1_purchase: int = 0
    week_2_purchase: int = 0
    week_3_purchase: int = 0
    week_4_purchase: int = 0
    opening_balance: int = 0
    sales_forecast: int = 0
    ending_inventory: int = 0
    dos_days: float = 0.0
    version: str = "v1.0"

class MonthlyPlanCreate(MonthlyPlanBase):
    pass

class MonthlyPlan(MonthlyPlanBase):
    id: int
    created_at: datetime
    updated_at: datetime
    product: Optional[Product] = None
    
    class Config:
        from_attributes = True

# System Config schemas
class SystemConfigBase(BaseModel):
    config_key: str
    config_value: str
    description: Optional[str] = None

class SystemConfigCreate(SystemConfigBase):
    pass

class SystemConfig(SystemConfigBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Response schemas
class MessageResponse(BaseModel):
    message: str

class DashboardStats(BaseModel):
    total_products: int
    active_products: int
    total_inventory_value: int
    low_stock_items: int
    pending_purchase_orders: int