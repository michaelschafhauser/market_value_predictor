import os
import joblib
from market_value_predictor.params import BUCKET_NAME
from google.cloud import storage


def download_model(bucket=BUCKET_NAME, rm=False):
    client = storage.Client().bucket(bucket)

    storage_location = "models/predictor/v1/model.joblib"
    blob = client.blob(storage_location)
    blob.download_to_filename("model.joblib")
    print("=> pipeline downloaded from storage")
    model = joblib.load("model.joblib")
    if rm:
        os.remove("model.joblib")
    return model


if __name__ == "__main__":
    download_model()
