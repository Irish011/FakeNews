import pickle
import re
import nltk
import fastapi
from fastapi import FastAPI
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import string
import os

nltk.download('stopwords')

file_path = os.path.abspath("Routes/tfidf_vectorizer.pkl")
file_path2 = os.path.abspath("Routes/automl_model.pkl")

with open(file_path, 'rb') as file:
    vectorizer = pickle.load(file)

with open(file_path2, 'rb') as file:
    model = pickle.load(file)

stopwords = nltk.corpus.stopwords.words('english')

def clean_text(text):
    text = "".join([word.lower() for word in text if word not in string.punctuation])
    tokens = re.split('\W+', text)
    text = [word for word in tokens if word not in stopwords]
    return " ".join(text)

app2 = FastAPI()



