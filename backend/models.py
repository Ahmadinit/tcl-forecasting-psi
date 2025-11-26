from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Date, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class ProductModel(Base):
    """Product master data - 销售型号"""
    __tablename__ = "product_models"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)  # 32S55, 43S55, etc.
    name = Column(String(100), nullable=False)
    shipping_mode = Column(String(20), nullable=False)  # CKD F, CBU, etc.
    status = Column(String(50), nullable=False)  # 25年产品, 26年新品
    remarks = Column(Text, nullable=True)  # 首批整机, etc.
    safety_stock_days = Column(Integer, default=45)  # Target DOS days
    safety_threshold_percentage = Column(Float, default=20.0)  # Safety stock as % of current inventory (default 20%)
    lead_time_weeks = Column(Integer, default=10)  # Lead time in weeks (default 10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    inventory = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
    sales_forecasts = relationship("SalesForecast", back_populates="product", cascade="all, delete-orphan")
    purchase_orders = relationship("PurchaseOrder", back_populates="product", cascade="all, delete-orphan")
    monthly_plans = relationship("MonthlyPlan", back_populates="product", cascade="all, delete-orphan")

class Inventory(Base):
    """Current inventory levels - 可销售库存"""
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('product_models.id', ondelete='CASCADE'), nullable=False)
    current_stock = Column(Integer, default=0)
    cbu_in_hand = Column(Integer, default=0)  # Complete Built Units
    kits_in_factory = Column(Integer, default=0)  # Kits being assembled
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("ProductModel", back_populates="inventory")

class SalesRecord(Base):
    """Actual sales data - 销售实际数"""
    __tablename__ = "sales_records"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('product_models.id', ondelete='CASCADE'), nullable=False)
    sale_date = Column(Date, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    channel = Column(String(20), nullable=False)  # ecommerce, A101, wholesale
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    product = relationship("ProductModel")

class SalesForecast(Base):
    """Sales predictions - 销售预测"""
    __tablename__ = "sales_forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('product_models.id', ondelete='CASCADE'), nullable=False)
    forecast_date = Column(Date, nullable=False, index=True)  # The month being forecasted
    channel = Column(String(20), nullable=False)  # ecommerce, A101, wholesale, all
    quantity = Column(Integer, nullable=False)
    forecast_type = Column(String(20), nullable=False)  # 'SI' (strategy), 'BP' (business plan), 'actual'
    version = Column(String(10), nullable=False)  # 'v1.0', 'v1.1' for rolling updates
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    product = relationship("ProductModel", back_populates="sales_forecasts")
    
    # Unique constraint to prevent duplicates
    __table_args__ = (
        UniqueConstraint('product_id', 'forecast_date', 'channel', 'forecast_type', 'version', 
                        name='uq_sales_forecast'),
    )

class PurchaseOrder(Base):
    """Purchase orders and forecasts - 采购预测"""
    __tablename__ = "purchase_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('product_models.id', ondelete='CASCADE'), nullable=False)
    po_number = Column(String(50), unique=True, nullable=True)
    quantity = Column(Integer, nullable=False)
    forecasted_quantity = Column(Integer, nullable=True)  # Forecasted quantity for reference
    order_week = Column(Date, nullable=False, index=True)  # Week when PO is created (Saturday)
    order_date = Column(Date, nullable=True)  # Actual order date
    expected_delivery_week = Column(Date, nullable=True)  # Expected delivery week (Order Week + Lead Time)
    etd = Column(Date, nullable=True)  # Estimated Time of Departure
    eta = Column(Date, nullable=True)  # Estimated Time of Arrival
    status = Column(String(20), nullable=False, default='suggested')  # suggested, ordered, shipped, delivered, cancelled
    shipping_mode = Column(String(20), nullable=False)  # CKD F, etc.
    stage = Column(String(50), nullable=True, default='CKD Prepared')  # CKD Prepared, Booking, Shipped, Customs, Assembly
    stage_updated_at = Column(DateTime, nullable=True)  # When stage was last updated
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("ProductModel", back_populates="purchase_orders")

class MonthlyPlan(Base):
    """Monthly PSI planning - PSI表数据"""
    __tablename__ = "monthly_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('product_models.id', ondelete='CASCADE'), nullable=False)
    plan_month = Column(Date, nullable=False, index=True)  # First day of the month
    week_1_purchase = Column(Integer, default=0)
    week_2_purchase = Column(Integer, default=0)
    week_3_purchase = Column(Integer, default=0)
    week_4_purchase = Column(Integer, default=0)
    opening_balance = Column(Integer, default=0)
    sales_forecast = Column(Integer, default=0)
    ending_inventory = Column(Integer, default=0)
    dos_days = Column(Float, default=0.0)
    version = Column(String(10), nullable=False, default='v1.0')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("ProductModel", back_populates="monthly_plans")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('product_id', 'plan_month', 'version', name='uq_monthly_plan'),
    )

class SystemConfig(Base):
    """System configuration and lead times"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(50), unique=True, nullable=False)
    config_value = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class User(Base):
    """User authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)