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
def index(player_name):
    features = get_player_features(player_name)
    if features.empty:
        prediction = "No player match found. Retry."
    elif features.shape == (1, 1):
        prediction = "The player name you provided is not unique. Please respecify."
    else:
        model = joblib.load("model.joblib")
        prediction = model.predict(features)
        prediction = "£{:,.1f}".format(prediction[0])

    return {"prediction": prediction}
