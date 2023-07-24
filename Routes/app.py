import fastapi
import email_validator
import pickle
import nltk
import pandas as pd
import string
import re
from supervised import AutoML
from sklearn.feature_extraction.text import TfidfVectorizer
# from models import fakenewsdetector

from fastapi import FastAPI, Depends, HTTPException, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pydantic import EmailStr, BaseModel
from middleware.token_middleware import TestMiddleware
from models import userinfo
from sqlalchemy.orm import Session
from controller.controller import generate_token, get_hash, authenticate_user, get_db

nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('english')

app = FastAPI()

model = AutoML()
with open('automl-CatBoost-Data500.pkl', 'rb') as file:
    model=pickle.load(file)
    
def clean_text(text):
    text = "".join([word.lower() for word in text if word not in string.punctuation])
    tokens = re.split('\W+', text)
    text = [word for word in tokens if word not in stopwords]
    return text

class PredictionRequest(BaseModel):
    text:str

# Middleware to be used
app.add_middleware(TestMiddleware)

templates = Jinja2Templates(directory="view")


# def predict_news(text):
#     preprocessed_text = fakenewsdetector.clean_text(text)
    
#     predictions = model.predict(preprocessed_text)
    
#     return predictions


@app.post("/predict")
def predict(fake_news: PredictionRequest):
    text = fake_news.text
    cleaned_text = clean_text(text)
    
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([cleaned_text])
    prediction = model.predict(X.toarray())
    
    return {"prediction": prediction[0]}

@app.get("/register")
def registration_page(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


@app.post("/register")
def user_register(name: str = Form('name'), email: EmailStr = Form('email'), password: str = Form('password'), db: Session = Depends(get_db)):
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
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return response


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def user_login(email: str = Form('email'), password: str = Form("password")):
    if authenticate_user(email, password):
        token = generate_token(email)
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="token", value=token, httponly=True)
        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

# Using static method
# @app.get("/dashboard")
# def dashboard(request: Request, response: Response):
#     username = AuthenticationMiddleware.authMiddle(request, response)
#     if isinstance(username, Response): return username
#     print(username)
#     return f"Welcome {username}"


@app.get("/dashboard")
def user_dashboard(request: Request):
    username = request.state.username
    print(username)
    return f"Welcome {username}"

