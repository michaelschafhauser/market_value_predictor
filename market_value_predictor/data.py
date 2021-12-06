import pandas as pd

from google.cloud import storage
from market_value_predictor.params import BUCKET_NAME, BUCKET_TRAIN_DATA_PATH


def get_data_from_gcp():
    """method to get the training data (or a portion of it) from google cloud bucket"""
    client = storage.Client()
    path = f"gs://{BUCKET_NAME}/{BUCKET_TRAIN_DATA_PATH}"
    df = pd.read_csv(path)
    return df
