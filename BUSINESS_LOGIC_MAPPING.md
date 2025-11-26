# PSI System - Business Logic Mapping

This document maps the Excel sheet business requirements to the implemented software architecture.

## 📊 Sheet 1: "purchase FCST" (Purchase Forecast)

### Excel Structure:
- **Columns**: Sales Model, Shipping Mode, Status, Remarks, ETD Time, Weekly purchase quantities (52+ weeks)
- **Lead Time**: 73 days total (28 days order placement + 45 days shipping)
- **Status Tracking**: No FCST to order, Already ordered, Delayed shipments (green background, red bold text)

### Software Implementation:

**Database Model**: `PurchaseOrder` (backend/models.py)
```python
- product_id: Links to ProductModel
- quantity: Purchase quantity
- order_week: Week when PO is created
- etd: Estimated Time of Departure
- eta: Estimated Time of Arrival (ETD + 45 days shipping)
- status: "suggested", "ordered", "shipped", "delivered", "delayed"
- shipping_mode: "CKD F", etc.
- stage: "CKD materials", "booking", "shipped", "customs", "assembly", "CBU warehouse"
```

**API Endpoints**: `backend/routers/purchase.py`
- `GET /purchase` - List all purchase orders with filtering
- `POST /purchase/create` - Create new purchase order
- `GET /purchase/forecast` - Generate PO suggestions based on sales forecast
- `PUT /purchase/{po_id}` - Update purchase order status
- `DELETE /purchase/{po_id}` - Remove purchase order

**Configuration**: `backend/config.py`
- `ORDER_ADVANCE_DAYS: 28` - Days before ETD to place order
- `SHIPPING_DAYS: 45` - Sea freight duration
- `CUSTOMS_DAYS: 10` - Customs clearance
- `PRODUCTION_DAYS: 15` - Assembly to warehouse
- `LEAD_TIME_DAYS: 70` - Total lead time

**Frontend**: `frontend/src/pages/PurchaseOrders.jsx` - Purchase forecast interface

---

## 📈 Sheet 2: "PSI" - Main Dashboard

### Excel Structure:
- **Monthly View**: January through August
- **Weekly Breakdown**: W1-W4 for each month
- **Key Metrics**:
  - Open Balance (Opening inventory)
  - Available Sales Inventory (可销售库存)
  - Monthly Sales Forecast (当月销售预测)
  - Ending Inventory (截止库存)
  - DOS Days (DOS天数)

### Formulas:
```
Available Sales Inventory = SUM(Weekly Purchases) + Previous Month Ending Inventory
Ending Inventory = Available Sales Inventory - Monthly Sales Forecast
DOS Days = (Ending Inventory / Monthly Sales Forecast) * 30
```

### Software Implementation:

**Database Model**: `MonthlyPlan` (backend/models.py)
```python
- product_id: Links to ProductModel
- plan_month: First day of the month
- week_1_purchase, week_2_purchase, week_3_purchase, week_4_purchase: Weekly purchases
- opening_balance: Starting inventory
- sales_forecast: Predicted sales for the month
- ending_inventory: Remaining stock
- dos_days: Days of Supply
```

**Calculation Logic**: `backend/utils/calculations.py`
- `calculate_monthly_psi()` - Calculates monthly PSI metrics
- `calculate_dos()` - Calculates Days of Supply
- `get_opening_balance()` - Gets opening balance for the month
- `get_monthly_purchases()` - Sums weekly purchases
- `get_monthly_sales()` - Gets total sales for the month

**Target DOS Strategy**:
- New branches: 50-60 days (config: `TARGET_DOS_NEW`)
- Established branches: <45 days (config: `TARGET_DOS_ESTABLISHED`)

**Frontend**: `frontend/src/pages/Dashboard.jsx` - Main PSI dashboard

---

## 📦 Sheet 3: "N+3 rolling stock"

### Excel Structure:
- **SKU**: Product models
- **N+3 Stock**: Total projected stock for next 3 months
- **Components**:
  - CBU in hand (Complete Built Units in warehouse)
  - Kits in factory (CKD kits being assembled)
  - Coming stock plan (In-transit inventory)

### End-to-End Inventory Formula:
```
End-to-End Inventory = Branch finished goods + Factory kits + Sea shipping + Domestic ODF
```

### Software Implementation:

**Database Model**: `Inventory` (backend/models.py)
```python
- product_id: Links to ProductModel
- current_stock: Current inventory level
- cbu_in_hand: Complete Built Units in warehouse
- kits_in_factory: Kits being assembled
```

**Calculation Logic**: `backend/utils/calculations.py`
- `calculate_n_plus_3_stock()` - Projects stock for next 3 months
- Considers current stock + upcoming purchases (next 90 days)
- Filters purchase orders with status "ordered" or "shipped"

**Frontend**: Can be displayed in `Dashboard.jsx` or `Inventory.jsx`

---

## 🎯 Sheet 4: "Sales forecast"

### Excel Structure:

#### Section 1: All-Channel Sales Forecast (全渠道销售预测)
- **Channels**: E-commerce + A101 + Traditional wholesale
- **Monthly aggregation**: Jan-Jun forecasts
- **Rolling refresh**: N+6 months updated weekly
- **Actuals update**: Monthly when actual sales data comes in

#### Section 2: Sales BP (Sales Business Plan)
- **Annual planning**: Jan-Dec monthly targets
- **Channel breakdown**: Same three channels
- **Strategic planning**: Based on SO (Sales Order) forecasts

### Key Strategy Notes:
- "SI sales forecast based on SO sales forecast and strategy deduction"
- "Weekly rolling refresh N+6 sales forecast"
- "Update to actual numbers when monthly sales actuals come out"

### Software Implementation:

**Database Models**:
1. `SalesRecord` (backend/models.py) - Actual sales data
   ```python
   - product_id: Links to ProductModel
   - sale_date: Date of sale
   - quantity: Sales quantity
   - channel: "ecommerce", "A101", "wholesale"
   ```

2. `SalesForecast` (backend/models.py) - Sales predictions
   ```python
   - product_id: Links to ProductModel
   - forecast_date: The month being forecasted
   - channel: "ecommerce", "A101", "wholesale", "all"
   - quantity: Forecasted quantity
   - forecast_type: "SI" (strategy), "BP" (business plan), "actual"
   - version: "v1.0", "v1.1" for rolling updates
   ```

**API Endpoints**: `backend/routers/sales.py`
- `POST /sales` - Add sales record
- `GET /sales` - List all sales records with filtering
- `GET /sales/by_model/{model_id}` - Get sales by product model
- `GET /sales/summary` - Sales summary grouped by product
- `GET /sales/weekly` - Weekly sales data for forecasting

**Forecasting Engine**: `backend/utils/forecast.py`
- `calculate_weighted_moving_average()` - Uses weights [0.5, 0.3, 0.15, 0.05]
- `get_weekly_sales_data()` - Gets weekly sales data for forecasting
- `generate_purchase_forecast()` - Generates purchase forecast based on sales trends

**Frontend**: `frontend/src/pages/Sales.jsx` - Sales forecast input interface

---

## 🚀 Core Business Strategy Implementation

### 1. Lead Time Management

**Configuration**: `backend/config.py`
```python
lead_time_breakdown = {
    "shipping": 45,      # Sea freight
    "customs": 10,       # Customs clearance  
    "production": 15,    # Assembly to warehouse
    "order_advance": 28  # Days before ETD to place order
}
Total: 70 days (28 + 45 + 10 + 15 - overlap)
```

### 2. Forecasting Approach

**Configuration**: `backend/config.py`
```python
forecasting_strategy = {
    "period": "weekly",           # Weekly analysis cycles
    "horizon": "N+3_months",     # 3-month rolling forecast
    "refresh": "weekly",          # Weekly updates
    "weights": [0.5, 0.3, 0.15, 0.05],  # Weighted moving average
    "channels": ["ecommerce", "A101", "wholesale"]
}
```

**Implementation**: `backend/utils/forecast.py`
- Weighted moving average for sales forecasting
- Weekly data aggregation
- Multi-channel support

### 3. Inventory Optimization

**Configuration**: `backend/config.py`
```python
inventory_strategy = {
    "target_dos": {
        "new_branches": (50, 60),   # 50-60 days for new branches
        "established": (0, 45)      # <45 days for mature branches
    },
    "service_level": 0.95,          # Service level for safety stock
    "safety_stock": "calculated"     # Based on demand variability
}
```

**Implementation**: `backend/utils/calculations.py` & `backend/utils/forecast.py`
- DOS calculations
- Safety stock calculations based on demand variability
- Reorder point logic based on lead time and forecast

### 4. Purchase Order Logic

**Implementation**: `backend/routers/purchase.py`
```python
po_calculation = {
    "trigger": "weekly_analysis",
    "horizon": "10_weeks",  # Based on 70-day lead time
    "quantities": "based_on_sales_forecast_minus_current_stock",
    "status_tracking": ["suggested", "ordered", "shipped", "delivered", "delayed"]
}
```

**Shipment Tracking**: `backend/routers/shipments.py`
- Stage tracking: CKD materials → booking → shipped → customs → assembly → CBU warehouse
- Status updates based on shipment progress

---

## 📋 Implementation Status

### ✅ Phase 1: Core PSI Dashboard (Sheet 2) - COMPLETE
- [x] Monthly inventory planning
- [x] DOS calculations
- [x] Purchase vs sales balancing
- [x] Weekly breakdown (W1-W4)

### ✅ Phase 2: Purchase Forecasting (Sheet 1) - COMPLETE
- [x] Weekly PO suggestions
- [x] Lead time management (70 days)
- [x] Shipment status tracking
- [x] ETD/ETA calculations

### ✅ Phase 3: Multi-channel Sales (Sheet 4) - COMPLETE
- [x] Channel-specific forecasting (ecommerce, A101, wholesale)
- [x] Actual vs forecast tracking
- [x] Rolling N+6 predictions (via versioning)
- [x] Sales BP support (forecast_type: "BP")

### ✅ Phase 4: Inventory Projection (Sheet 3) - COMPLETE
- [x] End-to-end stock visibility
- [x] In-transit inventory tracking
- [x] N+3 stock projections
- [x] CBU and kits tracking

---

## 🔧 Additional Features Implemented

1. **Product Model Management** (`backend/routers/models_api.py`)
   - Add/remove/update product models
   - SKU management
   - Shipping mode configuration

2. **System Settings** (`backend/routers/settings_api.py`)
   - Adjust forecast weights
   - Modify lead times
   - Update DOS targets

3. **Export Capabilities** (`backend/utils/export_excel.py`, `export_pdf.py`)
   - Excel generation for reports
   - PDF generation for reports

4. **Authentication** (`backend/routers/auth.py`)
   - Simple login system (1 user)

5. **Electron Desktop App** (`frontend/src/packaging/electron-app/`)
   - Desktop application packaging
   - macOS .app generation support

---

## 📝 Notes

- All business logic from the 4 Excel sheets has been mapped to database models and API endpoints
- The system supports weekly rolling forecasts (N+3 for inventory, N+6 for sales)
- Multi-channel sales tracking is fully implemented
- Lead time management follows the 70-day supply chain timeline
- DOS optimization targets are configurable per branch type
- The system is ready for production use with proper error handling and validation

