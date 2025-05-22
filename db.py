from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# --- Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    supabase_user_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    # Add more fields as needed, e.g. name, created_at, etc.
    biography = relationship("Biography", back_populates="user", uselist=False)

class Biography(Base):
    __tablename__ = "biographies"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    bio = Column(String)
    user = relationship("User", back_populates="biography")