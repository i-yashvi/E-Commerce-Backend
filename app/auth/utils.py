from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.auth.models import User
from app.core.database import SessionLocal
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")  # extracts the token string from the header


# Password hashing
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Token creation
def create_access_token(data: dict, expires_minutes: int = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict, expires_days: int = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        days=expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# Token decoding 
def decode_token(token: str):  # extracts user data
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# --------------------------------------------------------------------------------------------------------------
# Role-Based Access Control (RBAC)

# 1. Require Specific Role
def require_role(role: str):  # higher-order function, returns a dependency function
    def role_dependency(user: User = Depends(get_current_user)) -> User:
        if user.role != role:
            raise HTTPException(status_code=403, detail="You do not have permission to access this resource")
        return user
    return role_dependency

# 2. Get Current User from JWT Token
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        db: Session = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        db.close()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    