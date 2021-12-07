import os
import joblib
from market_value_predictor.params import BUCKET_NAME
from google.cloud import storage
import requests
from requests.structures import CaseInsensitiveDict
from market_value_predictor.utils import flatten, rename_api_feature_columns
from market_value_predictor.data import get_matching_tables_from_gcp
import pandas as pd
import json
import numpy as np


def download_model(bucket=BUCKET_NAME, rm=False):
    client = storage.Client().bucket(bucket)

    storage_location = "models/predictor/v1/model.joblib"
    blob = client.blob(storage_location)
    blob.download_to_filename("model.joblib")
    # print("=> pipeline downloaded from storage")
    model = joblib.load("model.joblib")
    # print("model saved")
    if rm:
        os.remove("model.joblib")
    return model


def get_player_features(name):
    url = "https://futdb.app/api/players/search"


    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["X-AUTH-TOKEN"] = "6ee5d299-299c-480c-ba52-514607532d6a"
    headers["Content-Type"] = "application/json"

    api_call = {"name": name}

    data = json.dumps(api_call)

    resp = requests.post(url, headers=headers, data=data)
    if resp.json()["items"]:
        player_dict = resp.json()["items"][0]

        if len(resp.json()["items"]) > 2:
            return pd.DataFrame([0])

        else:
            flat_player_dict = flatten(player_dict)
            flat_player_dict.pop("traits")
            flat_player_dict.pop("specialities")
            flat_df = pd.DataFrame(flat_player_dict, index=[0])

            # renaming column headers to match model database
            flat_df = rename_api_feature_columns(flat_df)

            # deleting non matching columns with model database
            no_match = []
            for elem in list(flat_df.columns):
                if elem[:1]=="_":
                    no_match.append(elem)
            flat_df = flat_df.drop(columns=no_match)

            # adding back player traits
            traits = []
            for i in range(len(player_dict["traits"])):
                traits.append(player_dict["traits"][i]["name"])

            traits_joined = ", ".join(traits)
            flat_df["player_traits"] = traits_joined


            # replacing codes with strings
            clubs = pd.read_csv(
                "raw_data/matching_tables/data_clubs_matching_from_API.csv")
            leagues = pd.read_csv(
                "raw_data/matching_tables/data_leagues_matching_from_API.csv")
            nations = pd.read_csv(
                "raw_data/matching_tables/data_nations_matching_from_API.csv")

            flat_df.club_name = flat_df.club_name.map(
                lambda x: list(clubs.loc[clubs["id"]==x])[0])

            flat_df.league_name = flat_df.league_name.map(
                lambda x: list(leagues.loc[leagues["id"]==x])[0])

            flat_df.nationality = flat_df.nationality.map(
                lambda x: list(nations.loc[nations["id"]==x])[0])

            flat_df = flat_df.fillna(value=np.nan)

            for col in ["gk_diving", "gk_handling", "gk_kicking", "gk_positioning", "gk_reflexes"]:
                flat_df[col] = flat_df[col].astype(float)

            return flat_df
    else:
        return pd.DataFrame()


if __name__ == "__main__":
    player_name = input("input player name:     ")
    features = get_player_features(player_name)
    if features.empty:
        print("No player match found. Retry.")
    elif features.shape == (1,1):
        print("The player name you provided is not unique. Please respecify.")
    else:
        model = download_model()
        prediction = model.predict(features)
        formatted_prediction = "£{:,.1f}".format(prediction[0])

        print(f"Predicted market value: {formatted_prediction}")
