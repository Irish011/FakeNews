from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    password: str
    interests: str

class UserLogin(BaseModel):
    email: str
    password: str
