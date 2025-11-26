from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import dashboard, inventory, sales, purchase, shipments, models_api, settings_api, auth, monthly_plan, export

app = FastAPI(title="PSI Forecast System", version="1.0")

# CORS setup to allow requests from frontend
# In production (Electron), allow file:// protocol and localhost
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:8000",  # Backend itself
    "file://",                 # Electron file:// protocol
    "app://",                  # Electron app:// protocol
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins for Electron app
    allow_credentials=True,
    allow_methods=["*"],       # allow GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],       # allow all headers
)

# Register Routers
app.include_router(auth.router)
app.include_router(models_api.router)
app.include_router(sales.router)
app.include_router(inventory.router)
app.include_router(purchase.router)
app.include_router(monthly_plan.router)
app.include_router(shipments.router)
app.include_router(settings_api.router)
app.include_router(export.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {"message": "PSI System Backend Running!"}

# Entry point for PyInstaller
if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Get host and port from command line args or use defaults
    host = "127.0.0.1"
    port = 8000
    
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == "--host" and i + 1 < len(sys.argv):
                host = sys.argv[i + 1]
            elif arg == "--port" and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
    
    uvicorn.run(app, host=host, port=port)
