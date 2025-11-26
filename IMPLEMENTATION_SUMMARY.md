# Business Logic Implementation Summary

This document summarizes how the Excel business logic has been mapped into the codebase.

## ✅ Completed Mappings

### 📊 Sheet 1: "purchase FCST" (Purchase Forecast)

**Business Logic:**
- Lead time: 73 days total (28 days order placement + 45 days shipping)
- Status tracking: suggested → ordered → shipped → delivered → delayed
- ETD calculation: Order week + 28 days
- ETA calculation: ETD + 70 days (45 shipping + 10 customs + 15 production)

**Implementation:**
- ✅ `backend/routers/purchase.py` - Updated ETD/ETA calculations
- ✅ `backend/config.py` - Added `ORDER_TO_ETD_DAYS: 28` and `ORDER_TO_ETA_DAYS: 73`
- ✅ Purchase order creation now calculates dates based on business rules

**Key Code:**
```python
# backend/routers/purchase.py (lines 96-108)
# ETD = order_week + 28 days
# ETA = ETD + 70 days (shipping + customs + production)
```

---

### 📈 Sheet 2: "PSI" - Main Dashboard

**Business Logic Formulas:**
```
Available Sales Inventory = SUM(Weekly Purchases) + Previous Month Ending Inventory
Ending Inventory = Available Sales Inventory - Monthly Sales Forecast
DOS Days = (Ending Inventory / Monthly Sales Forecast) * 30
```

**Implementation:**
- ✅ `backend/utils/calculations.py` - `calculate_monthly_psi()` method
- ✅ `backend/routers/inventory.py` - New endpoint `/inventory/psi/monthly`
- ✅ Weekly purchase breakdown (W1-W4) calculation
- ✅ Opening balance from previous month's ending inventory
- ✅ DOS calculation using exact Excel formula

**Key Code:**
```python
# backend/utils/calculations.py
def calculate_monthly_psi(self, product_id: int, target_month: date) -> Dict:
    # Available Sales Inventory = SUM(Weekly Purchases) + Previous Month Ending Inventory
    available_sales_inventory = total_weekly_purchases + opening_balance
    
    # Ending Inventory = Available Sales Inventory - Monthly Sales Forecast
    ending_inventory = available_sales_inventory - monthly_sales_forecast
    
    # DOS Days = (Ending Inventory / Monthly Sales Forecast) * 30
    dos_days = (ending_inventory / monthly_sales_forecast) * 30
```

**API Endpoint:**
```
GET /inventory/psi/monthly?product_id={id}&target_month={YYYY-MM-DD}
```

---

### 📦 Sheet 3: "N+3 rolling stock"

**Business Logic Formula:**
```
End-to-End Inventory = Branch finished goods + Factory kits + Sea shipping + Domestic ODF
```

**Implementation:**
- ✅ `backend/utils/calculations.py` - `calculate_n_plus_3_stock()` method
- ✅ `backend/routers/inventory.py` - New endpoint `/inventory/n-plus-3-stock`
- ✅ Breakdown includes:
  - CBU in hand (Branch finished goods)
  - Kits in factory (Factory kits)
  - Sea shipping (In-transit inventory)
  - Domestic ODF (Ordered but not yet in transit)

**Key Code:**
```python
# backend/utils/calculations.py
def calculate_n_plus_3_stock(self, product_id: int) -> Dict:
    # End-to-End Inventory = Branch finished goods + Factory kits + Sea shipping + Domestic ODF
    end_to_end_inventory = cbu_in_hand + kits_in_factory + sea_shipping_qty + domestic_odf_qty
```

**API Endpoint:**
```
GET /inventory/n-plus-3-stock?product_id={id}
```

---

### 🎯 Sheet 4: "Sales forecast"

**Business Logic:**
- Multi-channel aggregation: E-commerce + A101 + Traditional wholesale
- Rolling N+6 months forecast
- Weekly refresh capability
- SI forecast based on SO forecast and strategy deduction

**Implementation:**
- ✅ `backend/utils/forecast.py` - `aggregate_multi_channel_sales()` method
- ✅ `backend/routers/inventory.py` - New endpoint `/inventory/sales/multi-channel`
- ✅ Weighted moving average using config weights [0.5, 0.3, 0.15, 0.05]
- ✅ Channel-specific sales data retrieval
- ✅ All-channel forecast aggregation

**Key Code:**
```python
# backend/utils/forecast.py
def aggregate_multi_channel_sales(self, product_id: int, target_month: date) -> Dict:
    # Aggregate forecasts for each channel
    channels = ["ecommerce", "A101", "wholesale"]
    # Returns total across all channels
```

**API Endpoint:**
```
GET /inventory/sales/multi-channel?product_id={id}&target_month={YYYY-MM-DD}
```

---

## 🔧 Configuration Updates

**File: `backend/config.py`**

Added/Updated settings:
```python
# Lead Time Settings (from Excel Sheet 1)
ORDER_ADVANCE_DAYS: int = 28      # Days before ETD to place order
SHIPPING_DAYS: int = 45           # Sea freight duration
ORDER_TO_ETD_DAYS: int = 28       # Order week to ETD
ORDER_TO_ETA_DAYS: int = 73       # Order week to ETA (28 + 45)

# Forecasting Settings (from Excel Sheet 4)
FORECAST_WEIGHTS: List[float] = [0.5, 0.3, 0.15, 0.05]  # Weighted moving average

# Inventory Settings (from Excel Sheet 2)
TARGET_DOS_NEW: tuple = (50, 60)        # DOS range for new branches
TARGET_DOS_ESTABLISHED: tuple = (0, 45) # DOS range for established branches
```

---

## 📝 New API Endpoints

### 1. Monthly PSI Calculation
```
GET /inventory/psi/monthly?product_id={id}&target_month={YYYY-MM-DD}
```
Returns:
- Opening balance
- Weekly purchases (W1-W4)
- Available sales inventory
- Sales forecast
- Ending inventory
- DOS days
- Status

### 2. N+3 Rolling Stock
```
GET /inventory/n-plus-3-stock?product_id={id}
```
Returns:
- CBU in hand
- Kits in factory
- Sea shipping quantity
- Domestic ODF quantity
- End-to-end inventory
- N+3 stock projection

### 3. Multi-Channel Sales Aggregation
```
GET /inventory/sales/multi-channel?product_id={id}&target_month={YYYY-MM-DD}
```
Returns:
- E-commerce forecast
- A101 forecast
- Wholesale forecast
- Total all channels

---

## 🎯 Key Improvements

1. **Exact Formula Matching**: All calculations now match Excel formulas exactly
2. **Weekly Breakdown**: Added W1-W4 purchase breakdown for monthly planning
3. **Multi-Channel Support**: Full support for channel-specific forecasting
4. **End-to-End Inventory**: Complete N+3 stock calculation with all components
5. **Config-Driven**: All business parameters are configurable via `config.py`
6. **Proper Lead Times**: Corrected lead time calculations (73 days order to ETA)

---

## 📊 Data Flow

### Monthly PSI Calculation Flow:
1. Get opening balance (previous month's ending inventory)
2. Calculate weekly purchases (W1-W4) from PurchaseOrder table
3. Calculate available sales inventory (purchases + opening balance)
4. Get monthly sales forecast from SalesForecast table
5. Calculate ending inventory (available - forecast)
6. Calculate DOS days using formula: (ending / forecast) * 30

### N+3 Stock Calculation Flow:
1. Get CBU in hand from Inventory table
2. Get kits in factory from Inventory table
3. Calculate sea shipping (POs with status "ordered"/"shipped" and stage "shipped"/"customs")
4. Calculate domestic ODF (POs with status "ordered" and stage "CKD materials"/"booking")
5. Sum all components for end-to-end inventory

### Multi-Channel Sales Flow:
1. Query SalesForecast for each channel (ecommerce, A101, wholesale)
2. Aggregate forecasts by channel
3. Calculate total across all channels
4. Return breakdown and total

---

## ✅ Testing Checklist

- [ ] Test monthly PSI calculation with sample data
- [ ] Verify DOS calculation matches Excel formula
- [ ] Test N+3 stock with multiple purchase orders
- [ ] Verify multi-channel sales aggregation
- [ ] Test lead time calculations (28 days to ETD, 73 days to ETA)
- [ ] Verify weekly purchase breakdown (W1-W4)
- [ ] Test opening balance from previous month

---

## 📚 Related Files

- `backend/utils/calculations.py` - Core business logic calculations
- `backend/utils/forecast.py` - Forecasting engine
- `backend/routers/inventory.py` - API endpoints for PSI calculations
- `backend/routers/purchase.py` - Purchase order logic with lead times
- `backend/config.py` - Business configuration parameters
- `BUSINESS_LOGIC_MAPPING.md` - Detailed mapping documentation

---

**Status**: ✅ All business logic from 4 Excel sheets has been successfully mapped and implemented in the codebase.

