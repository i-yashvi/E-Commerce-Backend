from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.auth.schemas import UserCreate, UserLogin, TokenResponse, Role
from app.auth.models import User
from app.auth.utils import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup")
def signup(request: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    new_user = User(
        name=request.name,
        email=request.email,
        hashed_password=hash_password(request.password),
        role=request.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully. Please sign in."}

@router.post("/signin", response_model=TokenResponse)
def signin(request: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

    access_token = create_access_token({"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
