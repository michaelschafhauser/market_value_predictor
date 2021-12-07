import pandas as pd
import os
from termcolor import colored
from google.cloud import storage
from market_value_predictor.params import (
    BUCKET_NAME,
    MODEL_NAME,
    MODEL_VERSION,
    BUCKET_TRAIN_DATA_PATH,
)


def get_data_from_gcp():
    """method to get the training data (or a portion of it) from google cloud bucket"""
    client = storage.Client()
    path = f"gs://{BUCKET_NAME}/{BUCKET_TRAIN_DATA_PATH}"
    df = pd.read_csv(path)
    return df


def get_matching_tables_from_gcp():
    client = storage.Client()
    path = f"gs://{BUCKET_NAME}/data"
    clubs = pd.read_csv(path + "/clubs_matching_from_API.csv")
    leagues = pd.read_csv(path + "/leagues_matching_from_API.csv")
    nations = pd.read_csv(path + "/nations_matching_from_API.csv")
    return clubs, leagues, nations


def storage_upload(rm=False):
    client = storage.Client().bucket(BUCKET_NAME)

    local_model_name = "model.joblib"
    storage_location = f"models/{MODEL_NAME}/{MODEL_VERSION}/{local_model_name}"
    blob = client.blob(storage_location)
    blob.upload_from_filename("model.joblib")
    print(
        colored(
            f"=> model.joblib uploaded to bucket {BUCKET_NAME} inside {storage_location}",
            "green",
        )
    )
    if rm:
        os.remove("model.joblib")
