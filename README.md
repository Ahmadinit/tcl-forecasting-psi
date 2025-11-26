```
psi-app/
│
├── backend/                          # FastAPI Backend
│   │
│   ├── main.py                       # FastAPI main entry point
│   ├── database.py                   # SQLite connection + setup
│   ├── models.py                     # SQLAlchemy models (tables)
│   ├── schemas.py                    # Pydantic models (API validation)
│   ├── config.py                     # Settings (lead time, weights, etc.)
│   ├── init_db.py                    # Database initialization script
│   │
│   ├── routers/                      # All API endpoints grouped here
│   │   ├── inventory.py              # Inventory logic: add/update/subtract
│   │   ├── sales.py                  # Weekly/daily sales input endpoints
│   │   ├── purchase.py               # Forecast + PO suggestions
│   │   ├── shipments.py              # Track CKD, booking, shipped, etc.
│   │   ├── models_api.py             # Add/remove/update product models
│   │   ├── settings_api.py           # Adjust weights, formulas, lead time
│   │   └── auth.py                   # Simple login (1 user)
│   │
│   ├── utils/                        # Helper logic modules
│   │   ├── __init__.py
│   │   ├── forecast.py               # Weighted moving average, regression later
│   │   ├── calculations.py           # Inventory, DOS, safety stock logic
│   │   ├── export_excel.py           # Excel generation
│   │   ├── export_pdf.py             # PDF generation
│   │   └── shipments_helper.py       # Shipment stage status updates
│   │
│   └── data/
│       └── psi.db                    # SQLite database file
│
│
├── frontend/                         # React + Vite UI
│   ├── node_modules/ 
│   ├── src/
│   │   ├── components/               # Reusable UI components
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── AlertCard.jsx
│   │   │
│   │   ├── pages/                    # Screens
│   │   │   ├── Dashboard.jsx         # Main PSI dashboard (Sheet 2)
│   │   │   ├── Models.jsx            # Product model management
│   │   │   ├── Sales.jsx             # Sales forecast input (Sheet 4)
│   │   │   ├── Inventory.jsx         # Inventory management
│   │   │   ├── PurchaseOrders.jsx    # Purchase forecast (Sheet 1)
│   │   │   ├── Shipments.jsx         # Shipment tracking
│   │   │   ├── Settings.jsx          # System configuration
│   │   │   └── Login.jsx             # Authentication
│   │   │
│   │   ├── services/
│   │   │   └── api.js                # Axios calls centralized here
│   │   │
│   │   ├── packaging/
│   │   │   └── electron-app/         # Electron desktop app packaging
│   │   │       ├── main.js           # Electron main process
│   │   │       ├── preload.js        # Electron preload script
│   │   │       ├── package.json      # Electron package config
│   │   │       ├── icons.icns        # App icon for macOS
│   │   │       └── build/            # Output macOS .app generated later
│   │   │
│   │   ├── App.jsx                   # Main React app component
│   │   ├── index.css                 # Global styles
│   │   └── main.jsx                  # React entry point
│   │
│   ├── vite.config.js                # Vite configuration
│   ├── package.json                  # Frontend dependencies
│   ├── index.html                    # HTML entry point
│   └── package-lock.json             # Dependency lock file
│
│
├── venv/                             # Python virtual environment
│
├── database/                         # Additional database files (if any)
│
├── exports/                          # Generated Excel/PDF exports
│
└── readme.md                         # This file
```
