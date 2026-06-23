from app.cache import get_cache, set_cache, delete_cache
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.password_reset_token import PasswordResetToken
from app.schemas.user_schema import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest
)
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_refresh_token_expiry,
    create_password_reset_token,
    get_password_reset_token_expiry,
    get_current_user
)
from fastapi import Request
from app.utils.rate_limiter import rate_limit
from app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    LOGIN_RATE_LIMIT,
    REGISTER_RATE_LIMIT,
    FORGOT_PASSWORD_RATE_LIMIT,
    RATE_LIMIT_WINDOW_SECONDS
)

# from app.config import ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)



@router.post("/register", response_model=UserResponse)
def register_user(
    request: Request,
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    rate_limit(
        request=request,
        key_prefix="register",
        limit=REGISTER_RATE_LIMIT,
        window_seconds=RATE_LIMIT_WINDOW_SECONDS
    )

    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=TokenResponse)
def login_user(
    request: Request,
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    rate_limit(
        request=request,
        key_prefix="login",
        limit=LOGIN_RATE_LIMIT,
        window_seconds=RATE_LIMIT_WINDOW_SECONDS
    )
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    refresh_token_value = create_refresh_token()

    refresh_token = RefreshToken(
        token=refresh_token_value,
        user_id=user.id,
        expires_at=get_refresh_token_expiry()
    )

    db.add(refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_value,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token
    ).first()

    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    if stored_token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked"
        )

    if stored_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )

    user = db.query(User).filter(
        User.id == stored_token.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    stored_token.is_revoked = True

    new_access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    new_refresh_token_value = create_refresh_token()

    new_refresh_token = RefreshToken(
        token=new_refresh_token_value,
        user_id=user.id,
        expires_at=get_refresh_token_expiry()
    )

    db.add(new_refresh_token)
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token_value,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout_user(
    token_data: LogoutRequest,
    db: Session = Depends(get_db)
):
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token
    ).first()

    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found"
        )

    stored_token.is_revoked = True

    db.commit()

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(
    request: Request,
    request_data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    rate_limit(
        request=request,
        key_prefix="forgot_password",
        limit=FORGOT_PASSWORD_RATE_LIMIT,
        window_seconds=RATE_LIMIT_WINDOW_SECONDS
    )

    user = db.query(User).filter(
        User.email == request_data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )

    reset_token_value = create_password_reset_token()

    reset_token = PasswordResetToken(
        token=reset_token_value,
        user_id=user.id,
        expires_at=get_password_reset_token_expiry()
    )

    db.add(reset_token)
    db.commit()

    return {
        "message": "Password reset token generated successfully",
        "reset_token": reset_token_value
    }


@router.post("/reset-password")
def reset_password(
    request_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    stored_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == request_data.reset_token
    ).first()

    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid reset token"
        )

    if stored_token.is_used:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Reset token has already been used"
        )

    if stored_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Reset token has expired"
        )

    user = db.query(User).filter(
        User.id == stored_token.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.hashed_password = hash_password(request_data.new_password)
    delete_cache(f"user_profile:{user.id}")
    stored_token.is_used = True

    user_refresh_tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.is_revoked == False
    ).all()

    for token in user_refresh_tokens:
        token.is_revoked = True

    db.commit()

    return {
        "message": "Password reset successfully. Please login again."
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    cache_key = f"user_profile:{current_user.id}"

    cached_user = get_cache(cache_key)

    if cached_user:
        return cached_user

    user_data = {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }

    set_cache(cache_key, user_data)

    return user_data
