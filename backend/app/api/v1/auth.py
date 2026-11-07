"""
SIP Intelligence — Authentication API
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user_id,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.db.session import get_db
from app.models.users import User
from app.schemas import (
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and receive JWT tokens."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    user.last_login = datetime.now(timezone.utc)
    await db.flush()

    token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=body.email,
        full_name=body.full_name,
        hashed_password=get_password_hash(body.password),
        role=body.role,
        department_id=body.department_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    payload = verify_token(body.refresh_token, expected_type="refresh")
    user_id = payload.get("sub")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get the authenticated user's profile."""
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

