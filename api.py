from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, update
from supabase import Client
from typing import Annotated, Literal, Optional
from pydantic import BaseModel

# local imports
from dependencies import get_db, get_current_user, get_supabase_client
from schemas import UserCreate, BiographyCreate, BiographyOut
from db import User, Biography, Base
from settings import SupabaseSettings

# --- Lifespan Event Handler ---
async def lifespan(app: FastAPI):
    DATABASE_URL = "sqlite+aiosqlite:///./test.db"
    async_engine = create_async_engine(DATABASE_URL, echo=True)
    app.state.async_engine = async_engine
    app.state.async_sessionmaker = async_sessionmaker(
        bind=async_engine, expire_on_commit=False
    )
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    supabase: Client = Client(
        supabase_url=SupabaseSettings().supabase_url,
        supabase_key=SupabaseSettings().supabase_key,
    )
    app.state.supabase_client = supabase
    yield

# --- FastAPI Setup ---
app = FastAPI(lifespan=lifespan)

# --- Schemas for Auth ---
class AuthProviderRequest(BaseModel):
    provider: Literal["google", "github", "gitlab", "bitbucket", "azure", "facebook", "twitter", "discord", "twitch", "spotify", "slack", "linkedin", "apple"]
    redirect_to: Optional[str] = None  # Optional redirect URL

# --- Routes ---
@app.post("/register")
async def register(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    supabase_client: Annotated[Client, Depends(get_supabase_client)],
):
    result = supabase_client.auth.sign_up({"email": user.email, "password": user.password})
    if result.user is None:
        raise HTTPException(status_code=400, detail="Registration failed")
    local_user = User(supabase_user_id=result.user.id, email=user.email)
    db.add(local_user)
    await db.commit()
    await db.refresh(local_user)
    return {"msg": "User registered. Please check your email to confirm."}

@app.post("/login")
async def login(
    user: UserCreate,
    supabase_client: Annotated[Client, Depends(get_supabase_client)],
):
    result = supabase_client.auth.sign_in_with_password(
        {"email": user.email, "password": user.password}
    )
    if not result.session or not result.session.access_token:
        raise HTTPException(status_code=400, detail="Login failed")
    return {"access_token": result.session.access_token, "token_type": "bearer"}

@app.post("/login/oauth")
async def login_oauth(
    data: AuthProviderRequest,
    supabase_client: Annotated[Client, Depends(get_supabase_client)],
):
    # This returns a URL to redirect the user to the provider's login page
    response = supabase_client.auth.sign_in_with_oauth(
        {"provider": data.provider, "options": {"redirectTo": data.redirect_to} if data.redirect_to else {}}
    )
    # The response contains a URL to redirect the user to
    if not response or "url" not in response:
        raise HTTPException(status_code=400, detail="OAuth login failed")
    return {"auth_url": response["url"]}

@app.post("/biography", response_model=BiographyOut)
async def set_biography(
    bio: BiographyCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = update(Biography).where(Biography.user_id == current_user.id).values(bio=bio.bio)
    result = await db.execute(select(Biography).where(Biography.user_id == current_user.id))
    db_bio = result.scalar_one_or_none()
    if db_bio:
        db_bio.bio = bio.bio
    else:
        db_bio = Biography(user_id=current_user.id, bio=bio.bio)
        db.add(db_bio)
    await db.commit()
    await db.refresh(db_bio)
    return db_bio

@app.get("/biography", response_model=BiographyOut)
async def get_biography(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Biography).where(Biography.user_id == current_user.id))
    db_bio = result.scalar_one_or_none()
    if not db_bio:
        raise HTTPException(status_code=404, detail="Biography not found")
    return db_bio