from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from models import users
from fastapi.templating import Jinja2Templates

# from models.users import UserLogin

app = FastAPI()

SECRET_KEY = "87f2c2be95c484df33a2a438a8a0284bd0cf79d8497d1b53e20f3ba9162b5e6e"

ACCESS_TOKEN_EXPIRE = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

templates = Jinja2Templates(directory="view")


def create_token(data: dict, expire_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expire_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


@app.get("/register")
def reg(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


@app.post("/register")
async def register_user(credentials: users.UserLogin):
    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    access_token = create_token(data={"username": credentials.username}, expire_delta=expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/login")
async def user_login(credentials: users.UserLogin):
    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    access_token = create_token(data={"username": credentials.username}, expire_delta=expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("username")

        return {"message": f"Protected route accessed by {username}"}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
