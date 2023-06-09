import fastapi
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from models import users, userinfo
from fastapi.templating import Jinja2Templates
import email_validator
from passlib import hash

from sqlalchemy.orm import Session
from models.database import engine, sessionLocal

app = FastAPI()

userinfo.Base.metadata.create_all(engine)

SECRET_KEY = "87f2c2be95c484df33a2a438a8a0284bd0cf79d8497d1b53e20f3ba9162b5e6e"

ACCESS_TOKEN_EXPIRE = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

templates = Jinja2Templates(directory="view")


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_token(data: dict, expire_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expire_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


@app.get("/register")
def registration_page(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


pwd_hashing = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.get("/hash")
def get_hash(password: str):
    hash_pass = pwd_hashing.hash(password)
    return hash_pass


@app.post("/register")
# password hashing
# hashed_password = hash.bcrypt.hash(user.password)

def register_user(request: users.User, db: Session = Depends(get_db)):
    # email validation
    try:
        valid = email_validator.validate_email(email=users.User.email)

    except email_validator.EmailNotValidError:
        raise fastapi.HTTPException(status_code=404, detail="Invalid email")
    hashed_password = get_hash(request.password)
    user = userinfo.User(username=request.email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return "Registered Successfully"


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def user_login(credentials: users.UserLogin):
    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    access_token = create_token(data={"username": credentials.email}, expire_delta=expires)
    return {"access_token": access_token, "token_type": "bearer"}
