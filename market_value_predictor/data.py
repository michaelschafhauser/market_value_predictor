import pandas as pd

from google.cloud import storage
from market_value_predictor.params import BUCKET_NAME, BUCKET_TRAIN_DATA_PATH


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

if __name__ == "__main__":
    # get_matching_tables_from_gcp()
    pass
