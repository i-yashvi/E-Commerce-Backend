from fastapi import APIRouter, HTTPException, Security, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.auth.schemas import UserCreate, UserLogin, TokenResponse, Role, ForgotPasswordRequest, ResetPasswordRequest
from app.auth.models import User, PasswordResetToken
from app.auth.utils import hash_password, verify_password, create_access_token, create_refresh_token, require_role, get_current_user
from app.core.database import get_db
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

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


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    # Generate reset token
    reset_token = PasswordResetToken(user_id=user.id)
    db.add(reset_token)
    db.commit()

    # Simulate sending email (you can print or log it)
    print(f"[DEV] Reset Token for {user.email}: {reset_token.token}")

    return {"message": "Password reset link sent to your email (simulated)."}


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_record = db.query(PasswordResetToken).filter(PasswordResetToken.token == request.token).first()

    if not token_record:
        raise HTTPException(status_code=404, detail="Invalid token")
    if token_record.used or token_record.expiration_time < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired or already used")

    user = db.query(User).filter(User.id == token_record.user_id).first()
    user.hashed_password = hash_password(request.new_password)

    token_record.used = True
    db.commit()

    return {"message": "Password has been reset successfully."}


# -----------------------------------------------------------------------------------

@router.post("/admin-only")
def protected_admin_route(
    current_user: User = Depends(require_role("admin"))):  # Depends - Dependency Injection
    return {"message": f"Hello {current_user.name}, you are an admin!"}

@router.post("/user-only")
def protected_user_route(current_user: User = Depends(require_role("user"))):
    return {"message": f"Hello {current_user.name}, you are a user!"}
