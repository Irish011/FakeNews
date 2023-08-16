import fastapi
import email_validator
import pickle
import os

from fastapi import FastAPI, Depends, HTTPException, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pydantic import EmailStr
from models.cleaning import clean_text
from middleware.token_middleware import TestMiddleware
from models import userinfo
from sqlalchemy.orm import Session
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
from controller.controller import generate_token, get_hash, authenticate_user, get_db

app = FastAPI()

# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()

# drive = GoogleDrive(gauth)

# model_file_id = '10Pf6Hbz-tUSPp7oL6E1a2Cfau_an1I_U'
# model_file_1 = drive.CreateFile({'id': model_file_id})
# model_path = model_file_1.GetContentFile('automl_model.pkl')

# vectorizer_file_id = '1cYd3Su5JsM2DMsnBXP81wBeNJov-7NxB'
# vectorizer_file_1 = drive.CreateFile({'id': vectorizer_file_id})
# vectorizer_path = vectorizer_file_1.GetContentFile('tfidf_vectorizer.pkl')

# Middleware to be used
app.add_middleware(TestMiddleware)

templates = Jinja2Templates(directory="view")

# Local Downloaded File

vectorizer_path = os.path.abspath("C:\\Users\\Irish\\Downloads\\fakenewsproject\\tfidf_vectorizer.pkl")
model_path = os.path.abspath("C:\\Users\\Irish\\Downloads\\fakenewsproject\\automl_model.pkl")

with open(vectorizer_path, 'rb') as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

with open(model_path, 'rb') as model_file:
    model = pickle.load(model_file)


@app.get("/register")
def registration_page(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


@app.post("/register")
def user_register(name: str = Form('name'), email: EmailStr = Form('email'), password: str = Form('password'),
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


@app.get("/dashboard")
def user_dashboard(request: Request):
    username = request.state.username
    print(username)
    return f"Welcome {username}"


@app.get("/predict")
def predict_news(request: Request):
    return templates.TemplateResponse("dashBoard.html", {"request": request})


@app.post("/predict")
def predicted_news(request: Request, news: str = Form('news')):
    cleaned_text = clean_text(news)
    X = vectorizer.transform([cleaned_text])
    prediction = model.predict(X.toarray())

    prediction_result = "Real" if int(prediction[0]) == 0 else "Fake"

    return templates.TemplateResponse("dashBoard.html", {"request": request, "News_Prediction": prediction_result})


@app.get("/interests")
def load_interests(request: Request):
    return templates.TemplateResponse("interests.html", {"request": request})
