from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()

users = {}


class User(BaseModel):
    username: str
    password: str


security = HTTPBasic()


@app.post("/register")
def register_user(user: User):
    if user.username in users:
        return {"message": "Username not available"}

    users[user.username] = user.password
    return {"message": "User registered successfully"}

@app.post("/login")
def user_login(credentials: HTTPBasicCredentials):
    if credentials.username not in users or users[credentials.username] != credentials.password:
        return {"message": "Invalid User Credentials"}

    return {"message": "Successful Login!"}


