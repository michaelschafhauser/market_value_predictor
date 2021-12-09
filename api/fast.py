import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from market_value_predictor.predict import get_player_features
from market_value_predictor.utils import get_transfer_history
from forex_python.converter import CurrencyRates

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
    features, clean_player_name = get_player_features(player_name)

    if features.empty:
        prediction_eur = "No player match found. Retry."
        selected_features = {}

    elif features.shape == (1, 1):
        prediction_eur = "The player name you provided is not unique. Please respecify."
        selected_features = {}

    else:
        model = joblib.load("model.joblib")
        c = CurrencyRates()
        prediction_eur = model.predict(features) * float(c.get_rate('GBP', 'EUR'))
        if prediction_eur < 0:
            prediction_eur = "There are not enough observations to predict the value for this player"
            selected_features = {}

        else:
            prediction_eur = "EUR {:,.1f}m".format(prediction_eur[0])
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

    transfer_history = get_transfer_history(clean_player_name)

    return {
        "player_name": clean_player_name,
        "prediction": prediction_eur,
        "features": selected_features,
        "transfer_history": transfer_history
    }
