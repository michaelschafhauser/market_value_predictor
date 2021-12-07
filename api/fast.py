import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from market_value_predictor.predict import get_player_features

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
    return {"greeting": "Welcome to the market value predictor"}


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
        prediction = "GBP {:,.1f}".format(prediction[0])
        selected_features = features[
            [
                "overall",
                "pace",
                "shooting",
                "passing",
                "dribbling",
                "defending",
                "physic",
            ]
        ].to_dict(orient="list")

    return {"prediction": prediction, "features": selected_features}
