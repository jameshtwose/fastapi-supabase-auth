from pydantic_settings import BaseSettings

class SupabaseSettings(BaseSettings):
    supabase_url: str
    supabase_key: str

    class Config:
        env_file = ".env"