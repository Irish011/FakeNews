import fastapi
from fastapi import FastAPI, Depends, HTTPException, Request, Response, Form, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
import jwt
from passlib.context import CryptContext
from models import users, userinfo

import email_validator
from pydantic import EmailStr
from passlib import hash

# from middleware.token_middleware import TokenMiddleware
from middleware.token_middleware import TestMiddleware
from middleware.token_middleware import AuthenticationMiddleware

from sqlalchemy.orm import Session
from models.database import engine, sessionLocal

app = FastAPI()

app.add_middleware(TestMiddleware)

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


def generate_token(emailid: str) -> str:
    payload = {"emailID": emailid}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


@app.get("/register")
def registration_page(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


def get_hash(password: str):
    pwd_hashing = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash_pass = pwd_hashing.hash(password)
    return hash_pass


@app.post("/register")
def register_user(name: str = Form('name'), email: EmailStr = Form('email'), password: str = Form('password'),
                  db: Session = Depends(get_db)):
    # email validation
    try:
        valid = email_validator.validate_email(email=email)

    except email_validator.EmailNotValidError:
        raise fastapi.HTTPException(status_code=404, detail="Invalid email")

    # Password Hashing
    hashed_password = get_hash(password)
    user = userinfo.User(name=name, email=valid.email, password=hashed_password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return "valid"


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


def verify_hash(password: str, hash_password: str) -> bool:
    pass_hash = CryptContext(schemes=["bcrypt"])
    return pass_hash.verify(password, hash_password)


def authenticate_user(email: str, password: str) -> bool:
    db = sessionLocal()
    user = db.query(userinfo.User).filter(userinfo.User.email == email).first()
    db.close()
    if user and verify_hash(password, user.password):
        return True
    return False


@app.post("/login")
def user_login(email: str = Form('email'), password: str = Form("password")):
    if authenticate_user(email, password):
        token = generate_token(email)
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="token", value=token, httponly=True)
        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


@app.get("/")
def home(request: Request):
    return 'Welcome'


@app.get("/dashboard")
def dashboard(request: Request, response: Response):
    username = AuthenticationMiddleware.authMiddle(request, response)
    if isinstance(username, Response): return username
    print(username)
    return f"Welcome {username}"


@app.get("/testing")
def controll_test(request: Request):
    print(request)
    return {"message": "working"}
