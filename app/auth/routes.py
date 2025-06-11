from fastapi import APIRouter, Form, HTTPException, Security, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.auth.schemas import UserCreate, UserLogin, TokenResponse, Role, ForgotPasswordRequest, ResetPasswordRequest
from app.auth.models import User, PasswordResetToken
from app.auth.utils import hash_password, verify_password, create_access_token, create_refresh_token, require_role, get_current_user
from app.core.database import get_db
from datetime import datetime
from app.core.email import send_email

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")


# Sign-up using email, password & role
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


# Sign-in using unique email
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


# Forget password, get reset password link on your mail
@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    # Generate reset token
    reset_token = PasswordResetToken(user_id=user.id)  # Reset token stored in DB
    db.add(reset_token)
    db.commit()

    # Create reset password link 
    reset_link = f"http://localhost:8000/auth/reset-password-form?token={reset_token.token}"
    body = f"""  
    <h3>Password Reset Requested</h3>
    <p>Click the link below to reset your password:</p>
    <a href="{reset_link}">{reset_link}</a>
    <p>This link will expire in 30 minutes.</p>
    """
    # Send email on user-email for creating new password
    send_email(user.email, "Reset your password", body)

    # Simulate sending email
    print(f"[DEV] Reset Token for {user.email}: {reset_token.token}")

    return {"message": "Password reset link sent to your email."}


# When clicked on new password generation link sent on email, token and new password sent to reset_password API
@router.get("/reset-password-form")
def reset_password_form(token: str):
    html_content = f"""
    <html>
        <body>
            <h2>Reset Your Password</h2>
            <form method="post" action="/auth/reset-password">
                <input type="hidden" name="token" value="{token}">
                <label>New Password:</label><br>
                <input type="password" name="new_password" required><br><br>
                <button type="submit">Reset Password</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# New password created, DB updated
@router.post("/reset-password")
def reset_password(
    token: str = Form(...), 
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    token_record = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()

    if not token_record:
        return HTMLResponse(content="<h3>Invalid token.</h3>", status_code=404)
    if token_record.used or token_record.expiration_time < datetime.utcnow():
        return HTMLResponse(content="<h3>Token expired or already used.</h3>", status_code=400)

    user = db.query(User).filter(User.id == token_record.user_id).first()
    user.hashed_password = hash_password(new_password)
    token_record.used = True
    db.commit()

    return HTMLResponse(content="<h3>Password has been reset successfully.</h3>", status_code=200)


# -----------------------------------------------------------------------------------

@router.post("/admin-only")
def protected_admin_route(
    current_user: User = Depends(require_role("admin"))):  # Depends - Dependency Injection
    return {"message": f"Hello {current_user.name}, you are an admin!"}

@router.post("/user-only")
def protected_user_route(current_user: User = Depends(require_role("user"))):
    return {"message": f"Hello {current_user.name}, you are a user!"}
