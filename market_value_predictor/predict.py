import pandas as pd
import numpy as np
import joblib
import json
import requests
from requests.structures import CaseInsensitiveDict
from google.cloud import storage
from market_value_predictor.params import BUCKET_NAME
from market_value_predictor.utils import flatten, rename_api_feature_columns
import os
from dotenv import load_dotenv
load_dotenv()


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
    headers["X-AUTH-TOKEN"] = os.getenv("API_TOKEN")
    headers["Content-Type"] = "application/json"

    api_call = {"name": name}

    data = json.dumps(api_call)

    # get clean name here

    resp = requests.post(url, headers=headers, data=data)

    if resp.json()["items"]:

        temp_list = []
        for i in range(resp.json()["count"]):
            temp_list.append(resp.json()["items"][i]["resource_base_id"])
        num_of_players = len(set(temp_list))


        player_base_id = temp_list[0]

        temp_list = []
        for j in range(resp.json()["count"]):
            temp_list.append(resp.json()["items"][j]["resource_id"])
        card_index = temp_list.index(player_base_id)

        player_dict = resp.json()["items"][card_index]

        if num_of_players > 1:
            return pd.DataFrame([0]), "The player name you provided is not unique. Please respecify."

        else:
            clean_player_name = player_dict["name"]
            flat_player_dict = flatten(player_dict)
            flat_player_dict.pop("traits")
            flat_player_dict.pop("specialities")
            flat_df = pd.DataFrame(flat_player_dict, index=[0])

            # renaming column headers to match model database
            flat_df = rename_api_feature_columns(flat_df)

            # deleting non matching columns with model database
            no_match = []
            for elem in list(flat_df.columns):
                if elem[:1] == "_":
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
                "raw_data/matching_tables/data_clubs_matching_from_API.csv"
            )
            leagues = pd.read_csv(
                "raw_data/matching_tables/data_leagues_matching_from_API.csv"
            )
            nations = pd.read_csv(
                "raw_data/matching_tables/data_nations_matching_from_API.csv"
            )

            flat_df.club_name = flat_df.club_name.map(
                lambda x: list(clubs.loc[clubs["id"] == x].name)[0]
            )

            flat_df.league_name = flat_df.league_name.map(
                lambda x: list(leagues.loc[leagues["id"] == x].name)[0]
            )

            flat_df.nationality = flat_df.nationality.map(
                lambda x: list(nations.loc[nations["id"] == x].name)[0]
            )

            flat_df = flat_df.fillna(value=np.nan)

            for col in [
                "gk_diving",
                "gk_handling",
                "gk_kicking",
                "gk_positioning",
                "gk_reflexes",
            ]:
                flat_df[col] = flat_df[col].astype(float)

            return flat_df, clean_player_name
    else:
        return pd.DataFrame(), "No player found"


if __name__ == "__main__":
    player_name = input("input player name:     ")
    features = get_player_features(player_name)
    if features.empty:
        print("No player match found. Retry.")
    elif features.shape == (1, 1):
        print("The player name you provided is not unique. Please respecify.")
    else:
        model = download_model()
        prediction = model.predict(features)
        formatted_prediction = "£{:,.1f}".format(prediction[0])
        print(list(features.columns))

        print(f"Predicted market value: {formatted_prediction}")
