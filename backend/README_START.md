# How to Start the Backend

## ✅ Venv Setup (Already Done)

The virtual environment is located at `backend/venv/`. This is the **correct** location - having venv inside the backend folder keeps dependencies isolated per project.

## 📦 All Packages Installed

All required packages from `requirements.txt` are already installed in the venv:
- ✅ fastapi==0.110.0
- ✅ uvicorn==0.29.0
- ✅ pydantic==1.10.13
- ✅ sqlalchemy==2.0.32
- ✅ numpy==1.26.4
- ✅ pandas==2.2.2
- ✅ scikit-learn==1.4.2
- ✅ openpyxl==3.1.2
- ✅ reportlab==4.0.7
- ✅ All other dependencies

## 🚀 Starting the Backend

### Option 1: Using the Startup Script (Easiest)

**Windows (PowerShell):**
```powershell
cd backend
.\start_backend.ps1
```

**Windows (Command Prompt):**
```cmd
cd backend
start_backend.bat
```

### Option 2: Manual Start

**Windows:**
```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**Or activate venv first:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Option 3: Direct Python Execution

```powershell
cd backend
.\venv\Scripts\python.exe main.py
```

## ✅ Verification

Once started, you should see:
- Server running on `http://127.0.0.1:8000`
- API docs at `http://127.0.0.1:8000/docs`
- Root endpoint: `http://127.0.0.1:8000/` returns `{"message": "PSI System Backend Running!"}`

## 📝 Notes

1. **Venv Location**: Having `venv/` inside `backend/` is correct and recommended for project isolation
2. **All packages are installed** - no need to run `pip install` again
3. **Database**: SQLite database is at `backend/data/psi.db` and will be created automatically

