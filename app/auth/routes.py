from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timezone
from app.core.config import settings
from app.auth.schemas import ResetPasswordRequest, UserCreate, UserLogin, TokenResponse, ForgotPasswordRequest, RefreshTokenRequest
from app.auth.models import User, PasswordResetToken
from app.auth.utils import hash_password, verify_password, create_access_token, create_refresh_token, require_role
from app.core.database import get_db
from app.core.email import send_email
from app.core.logger import logger  

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")


# Sign-up using email, password & role
@router.post("/signup")
def signup(request: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Signup attempt: {request.email}")
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        logger.warning(f"Signup failed - Email already registered: {request.email}")
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

    logger.info(f"User created successfully: {request.email}")
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully. Please sign in."}


# Sign-in using unique email
@router.post("/signin", response_model=TokenResponse)
def signin(request: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Signin attempt: {request.email}")
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        logger.warning(f"Signin failed for: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

    access_token = create_access_token({"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.email})

    logger.info(f"Signin successful for: {request.email}")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


# Forget password, get reset password link on your mail
@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    logger.info(f"Forgot password request for: {request.email}")
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        logger.warning(f"Forgot password - Email not found: {request.email}")
        raise HTTPException(status_code=404, detail="Email not found")

    reset_token = PasswordResetToken(user_id=user.id)  # Generate reset token
    db.add(reset_token)  # Reset token stored in DB
    logger.debug(f"Password reset token generated for {request.email}: {reset_token.token}")
    db.commit()

    # Create reset password link 
    reset_link = f"http://localhost:8000/auth/reset-password-form?token={reset_token.token}"
    body = f"""  
    <h3>Password Reset Requested</h3>
    <p>Click the link below to reset your password:</p>
    <a href="{reset_link}">{reset_link}</a>
    <p>This link will expire in 30 minutes.</p>
    """
    send_email(user.email, "Reset your password", body)  # Send email on user-email for creating new password

    logger.info(f"Reset email sent to {request.email}")
    return {"message": "Password reset link sent to your email.", "token": reset_token.token}


# Create new password, Update DB
@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    logger.info(f"Reset password attempt using token: {request.token}")
    token_record = db.query(PasswordResetToken).filter(PasswordResetToken.token == request.token).first()

    if not token_record:
        logger.warning(f"Reset failed - Invalid token: {request.token}")
        raise HTTPException(status_code=404, detail="Invalid token")
    elif token_record.used or token_record.expiration_time.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        logger.warning(f"Reset failed - Token expired or already used: {request.token}")
        raise HTTPException(status_code=400, detail="Token expired or already used")

    user = db.query(User).filter(User.id == token_record.user_id).first()
    user.hashed_password = hash_password(request.new_password)
    token_record.used = True
    db.commit()
    
    logger.info(f"Password successfully reset for user ID: {token_record.user_id}")
    return {"message": "Password has been reset successfully."}


# Refresh token regenerates access token after it expires
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")

        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token({"sub": email, "role": role})

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=request.refresh_token,
        token_type="bearer"
    )
