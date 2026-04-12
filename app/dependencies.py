from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.security import decode_access_token
from app.common.exceptions import ForbiddenException, UnauthorizedException
from app.database import async_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise UnauthorizedException(
                code="INVALID_TOKEN",
                message="Token payload is invalid.",
            )
        user_id = int(sub)
    except JWTError:
        raise UnauthorizedException(
            code="INVALID_TOKEN",
            message="Token is invalid or expired.",
        ) from None
    except (TypeError, ValueError):
        raise UnauthorizedException(
            code="INVALID_TOKEN",
            message="Token payload is invalid.",
        ) from None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise UnauthorizedException(
            code="INVALID_TOKEN",
            message="User no longer exists.",
        )
    return user


async def require_doctor(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    if user.role != "doctor":
        raise ForbiddenException(
            code="DOCTOR_REQUIRED",
            message="This action requires a doctor account.",
        )
    return user


async def require_patient(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    if user.role != "patient":
        raise ForbiddenException(
            code="PATIENT_REQUIRED",
            message="This action requires a patient account.",
        )
    return user
