from pydantic import BaseModel
from pydantic.alias_generators import to_camel

class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        alias_generator = to_camel
        # This will convert snake_case to camelCase for JSON serialization
        

class UserCreate(BaseSchema):
    email: str
    password: str

class UserOut(BaseSchema):
    id: int
    supabase_user_id: str
    email: str

class BiographyCreate(BaseSchema):
    bio: str

class BiographyOut(BaseSchema):
    user_id: int
    bio: str