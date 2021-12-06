from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pytz
from datetime import datetime
import joblib
from predict import download_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def index():
    return {"greeting": "Hello world"}


@app.get("/predict")
def index(player_name):
    # get player features from API

    # bring player features in required format

    # load model
    model = download_model()

    # make prediction using loaded model
    prediction = model.predict(df)[0]

    return {"prediction": "prediction"}
