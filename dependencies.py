from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# local imports
from db import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Dependency ---
async def get_db(request: Request):
    async_sessionmaker = request.app.state.async_sessionmaker
    async with async_sessionmaker() as db:
        yield db

async def get_supabase_client(request: Request):
    return request.app.state.supabase_client

# --- Auth Helpers ---
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
    supabase_client=Depends(get_supabase_client),
) -> User:
    # Validate JWT with Supabase
    try:
        user = supabase_client.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        stmt = select(User).where(User.supabase_user_id == user.user.id)
        result = await db.execute(stmt)
        local_user = result.scalar_one_or_none()
        if not local_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found in local DB",
            )
        return local_user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )