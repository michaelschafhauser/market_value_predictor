from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pytz
from datetime import datetime
import joblib
from predict import download_model
from predict import get_player_features

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
def index():

    player_name=input("Please name a football player:   ")

    # get player features from API
    features = get_player_features(player_name)

    # load model
    model = download_model()

    # make prediction using loaded model
    prediction = model.predict(features)[0]

    return {"prediction": prediction}
