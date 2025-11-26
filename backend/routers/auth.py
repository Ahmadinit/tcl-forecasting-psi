from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from database import get_db
from models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str

class MessageResponse(BaseModel):
    message: str

class LoginResponse(BaseModel):
    message: str
    user_id: int
    username: str

# POST: Create user (for initial setup)
@router.post("/create", response_model=MessageResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user (simple authentication for now)"""
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # In a real app, you should hash the password!
    user = User(
        username=payload.username,
        password_hash=payload.password  # This should be hashed in production!
    )
    db.add(user)
    db.commit()
    
    return {"message": "User created successfully"}

# POST: Login
@router.post("/login", response_model=LoginResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """User login (simple authentication for now)"""
    user = db.query(User).filter(
        User.username == payload.username,
        User.password_hash == payload.password  # This should verify hashed password in production!
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=401, detail="User account is inactive")
    
    # Update last login
    user.last_login = datetime.now()  # type: ignore[assignment]
    db.commit()
    
    return {
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username
    }

# GET: Check if user exists (for initial setup)
@router.get("/check-setup")
def check_setup(db: Session = Depends(get_db)):
    """Check if any users exist (for initial setup)"""
    user_count = db.query(User).count()
    return {
        "is_setup": user_count > 0,
        "user_count": user_count
    }

# GET: User info
@router.get("/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at is not None else None,  # type: ignore[union-attr]
        "last_login": user.last_login.isoformat() if user.last_login is not None else None  # type: ignore[union-attr]
    }