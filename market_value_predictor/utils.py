import collections.abc
import pandas as pd
# from forex_python.converter import CurrencyRates
import json
import requests
from requests.structures import CaseInsensitiveDict
import os
from dotenv import load_dotenv
import requests
from requests.structures import CaseInsensitiveDict
import io
from PIL import Image

load_dotenv()


def position_field_transform(pos):
    return int(pos.split("+")[0])


def flatten(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def rename_api_feature_columns(df):
    df = df.rename(
        columns={
            "id": "_id",
            "resource_id": "_resource_id",
            "name": "_name",
            "age": "age",
            "resource_base_id": "_resource_base_id",
            "fut_bin_id": "_fut_bin_id",
            "fut_wiz_id": "_fut_wiz_id",
            "first_name": "_first_name",
            "last_name": "_last_name",
            "common_name": "_common_name",
            "height": "height_cm",
            "weight": "weight_kg",
            "birth_date": "_birth_date",
            "league": "league_name",
            "nation": "nationality",
            "club": "club_name",
            "rarity": "_rarity",
            "position": "team_position",
            "skill_moves": "skill_moves",
            "weak_foot": "weak_foot",
            "foot": "preferred_foot",
            "attack_work_rate": "_attack_work_rate",
            "defense_work_rate": "_defense_work_rate",
            "total_stats": "_total_stats",
            "total_stats_in_game": "_total_stats_in_game",
            "rating": "overall",
            "rating_average": "_rating_average",
            "pace": "pace",
            "shooting": "shooting",
            "passing": "passing",
            "dribbling": "dribbling",
            "defending": "defending",
            "physicality": "physic",
            "pace_attributes_acceleration": "movement_acceleration",
            "pace_attributes_sprint_speed": "movement_sprint_speed",
            "shooting_attributes_positioning": "mentality_positioning",
            "shooting_attributes_finishing": "attacking_finishing",
            "shooting_attributes_shot_power": "power_shot_power",
            "shooting_attributes_long_shots": "power_long_shots",
            "shooting_attributes_volleys": "attacking_volleys",
            "shooting_attributes_penalties": "mentality_penalties",
            "passing_attributes_vision": "mentality_vision",
            "passing_attributes_crossing": "attacking_crossing",
            "passing_attributes_free_kick_accuracy": "skill_fk_accuracy",
            "passing_attributes_short_passing": "attacking_short_passing",
            "passing_attributes_long_passing": "skill_long_passing",
            "passing_attributes_curve": "skill_curve",
            "dribbling_attributes_agility": "movement_agility",
            "dribbling_attributes_balance": "movement_balance",
            "dribbling_attributes_reactions": "movement_reactions",
            "dribbling_attributes_ball_control": "skill_ball_control",
            "dribbling_attributes_dribbling": "skill_dribbling",
            "dribbling_attributes_composure": "mentality_composure",
            "defending_attributes_interceptions": "mentality_interceptions",
            "defending_attributes_heading_accuracy": "attacking_heading_accuracy",
            "defending_attributes_standing_tackle": "defending_standing_tackle",
            "defending_attributes_sliding_tackle": "defending_sliding_tackle",
            "physicality_attributes_jumping": "power_jumping",
            "physicality_attributes_stamina": "power_stamina",
            "physicality_attributes_strength": "power_strength",
            "physicality_attributes_aggression": "mentality_aggression",
            "goalkeeper_attributes_diving": "gk_diving",
            "goalkeeper_attributes_handling": "gk_handling",
            "goalkeeper_attributes_kicking": "gk_kicking",
            "goalkeeper_attributes_positioning": "gk_positioning",
            "goalkeeper_attributes_reflexes": "gk_reflexes",
        }
    )

    return df


usable_columns = [
    "fee_cleaned",
    "age",
    "height_cm",
    "weight_kg",
    "league_name",
    "nationality",
    "club_name",
    "team_position",
    "skill_moves",
    "weak_foot",
    "preferred_foot",
    "overall",
    "pace",
    "shooting",
    "passing",
    "dribbling",
    "defending",
    "physic",
    "movement_acceleration",
    "movement_sprint_speed",
    "mentality_positioning",
    "attacking_finishing",
    "power_shot_power",
    "power_long_shots",
    "attacking_volleys",
    "mentality_penalties",
    "mentality_vision",
    "attacking_crossing",
    "skill_fk_accuracy",
    "attacking_short_passing",
    "skill_long_passing",
    "skill_curve",
    "movement_agility",
    "movement_balance",
    "movement_reactions",
    "skill_ball_control",
    "skill_dribbling",
    "mentality_composure",
    "mentality_interceptions",
    "attacking_heading_accuracy",
    "defending_standing_tackle",
    "defending_sliding_tackle",
    "power_jumping",
    "power_stamina",
    "power_strength",
    "mentality_aggression",
    "gk_diving",
    "gk_handling",
    "gk_kicking",
    "gk_positioning",
    "gk_reflexes",
    "player_traits",
]


def get_transfer_history(player_name):
    df = pd.read_csv("raw_data/transfer_history_combined.csv")

    try:
        transfer_df = df.loc[(df["player_name"] == player_name)
        & (df["transfer_movement"] == "in")][[
            "player_name", "age", "club_name", "club_involved_name",
            "fee_cleaned", "season", "transfer_period"
        ]].rename(
            columns={
                "club_name": "receiving_club",
                "club_involved_name": "giving_club",
                "fee_cleaned": "transfer_fee"
            })

        c = CurrencyRates()

        transfer_df["transfer_fee"] = transfer_df.transfer_fee.map(
            lambda x: round(x*float(c.get_rate('GBP', 'EUR')), 2))

        if transfer_df.empty:
            transfer_dict = {"info": "no transfer history found"}
        else:
            transfer_dict = transfer_df.to_dict(orient="list")

    except:
        transfer_dict = {"info": "no transfer history found"}

    return transfer_dict


def get_player_id(player_name):
    url = "https://futdb.app/api/players/search"

    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["X-AUTH-TOKEN"] = os.getenv("API_TOKEN")
    headers["Content-Type"] = "application/json"

    api_call = {"name": player_name}

    data = json.dumps(api_call)

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
            return None

        else:
            return player_dict["id"]
    else:
        return None

def get_player_image(player_id):
    url = "https://futdb.app/api/players/"


    headers = CaseInsensitiveDict()
    headers["accept"] = "*/*"
    headers["X-AUTH-TOKEN"] = "6ee5d299-299c-480c-ba52-514607532d6a"

    response = requests.get(url + str(player_id) + "/image", headers=headers)

    in_memory_file = io.BytesIO(response.content)

    im = Image.open(in_memory_file)

    pic_path = "image/player_image.png"
    im.save(pic_path)

    return pic_path
