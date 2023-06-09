from pydantic import BaseModel


class User(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str
