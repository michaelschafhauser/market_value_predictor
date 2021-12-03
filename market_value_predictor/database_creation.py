# IMPORTS ---------------------
from collections import UserList
import pandas as pd
from pandas.core.reshape.concat import concat
import requests
from bs4 import BeautifulSoup
from utils import position_field_transform


# DATA RELATED FUNCTIONS ------
def get_data(filepath):
    '''
    Load the csv file from the raw_data directory
    '''
    df = pd.read_csv(filepath)
    return df


def transfer_cleaning(transfer_df):
    '''
    cleans the transfer_history_combined csv file to only have available
    players whose transfer fee information is available
    '''

    df = transfer_df

    ## dropping NaNs in fee_cleaned
    df = df.loc[df["fee_cleaned"].notna()]

    ## dropping 0.0 transfer fees
    df = df.loc[df["fee_cleaned"]!=0]

    ## dropping "in" vs. "out" duplications
    df = df.loc[df["transfer_movement"]!="out"]

    ## Selecting players from 2015 onwards
    df = df.loc[df["year"]>2014]

    ## If two transfers per year, keep only one with higher value
    df.sort_values(["year", "player_name", "club_name", "fee_cleaned"],
                          ascending=(True, True, True, False),
                          inplace=True)

    df = df.drop_duplicates(keep="first", subset=["player_name", "year", "club_name"])

    df["player_name"] = df["player_name"].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    df.drop(df.filter(regex="Unname"), axis=1, inplace=True)

    return df


def players_cleaning(players_df):

    # FEATURE ENG.1 : generate last name column from short name
    players_df["last_name"] = +players_df["short_name"].str.extract(
        r'\b(\w+)$', expand=True)

    # FEATURE ENG.2 : adding a first name column
    splited_name = players_df['long_name'].str.split(' ', 1)
    f_name = []
    first_names = []
    for _, value in splited_name.items():
        f_name.append(value)
    for i in range(len(f_name)):
        first_names.append(f_name[i][0])

    # create a datframe out of the first names
    fname_df = pd.DataFrame(first_names, columns=['first_name'])

    # concatenate the fname_df to the players_df
    players_df = pd.concat([players_df, fname_df], axis=1, sort=False)

    # concatenate a column with player first & last name
    players_df["player_name"] = players_df["first_name"] + " " + players_df[
        "last_name"]

    # process the player_name to lower case and no accents
    players_df["player_name"] = players_df["player_name"].str.lower().str.normalize(
        'NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    players_df.drop(players_df.filter(regex="Unname"), axis=1, inplace=True)

    players_df = players_df.drop(columns=["first_name", "last_name"])

    return players_df


def merge_by_name_only(transfer_df, players_df):
    merged_df = transfer_df.merge(players_df,
                                  left_on=["player_name", "year"],
                                  right_on=["player_name", "fifa year"],
                                  how='inner')

    merged_df = merged_df.drop_duplicates(subset=["player_name", "year"],
                                          keep=False)

    return merged_df


def add_sofifa_id_to_non_matched_transfers(transfer_df, players_df):

    non_matched_transfers_df = transfer_df.merge(
        players_df[["sofifa_id", "player_name", "fifa year"]],
        left_on=["player_name", "year"],
        right_on=["player_name", "fifa year"],
        how='left')

    non_matched_transfers_df = non_matched_transfers_df.loc[
        non_matched_transfers_df["sofifa_id"].isnull()].drop(
            columns="fifa year")

    # non_matched_transfers_df = non_matched_transfers_df.iloc[:10]

    df = id_scrapping(non_matched_transfers_df, "player_name")

    df = df.loc[df["sofifa_id"] != 0]

    df["sofifa_id"] = df.sofifa_id.astype(int)

    return df


def id_scrapping(df, column_name):
    '''
    Scrapes the SOFIFA website for players id's via their name.
    players whose name dont get a match are attributed a 'Nan' value
    df: pass in a dataframe
    column_name: pass in the column name which contains the players name
    '''
    URL = "https://sofifa.com/players"

    df['sofifa_id'] = 0

    temp = []
    for _, name in enumerate(df[column_name]):
        params = {'keyword': name}
        response = requests.get(URL, params=params)
        soup = BeautifulSoup(response.content, 'html.parser')

        try:
            sofifa_ids = soup.find_all("img", class_="player-check")
            if len(sofifa_ids) == 1:
                temp.append(sofifa_ids[0].get('id'))
            else:
                temp.append("0")
        except AttributeError:
            temp.append("0")

    df["sofifa_id"] = temp

    return df


def merge_by_sofifa_id(transfer_df, players_df):
    merged_df = transfer_df.merge(players_df,
                                  left_on=["sofifa_id", "year"],
                                  right_on=["sofifa_id", "fifa year"],
                                  how='inner', )

    merged_df = merged_df.drop(columns=["player_name_y"])

    merged_df = merged_df.rename(columns={"player_name_x": "player_name"})

    return merged_df



def concat_datasets(merged_1_df, merged_2_df):
    return pd.concat([merged_1_df, merged_2_df])



def clean_master_df(df):
    df = df.drop(columns=['player_url', 'short_name', 'age_x', 'fee', 'value_eur'])

    df = df.rename(
        columns={
            "club_name_x": "receiving_club",
            "club_involved_name": "giving_club",
            "league_name_x": "receiving_league",
            "age_y": "age",
            'club_name_y': "club_name",
            'league_name_y': "league_name"
        })

    # Change dtypes
    df["joined"] = pd.to_datetime(df.joined)
    df["dob"] = pd.to_datetime(df.dob)

    # Creating new columns based on initial ones to remove initial ones thereafter
    df.reset_index(inplace=True, drop=True)
    df["national_team"] = df.nation_jersey_number.map(
        lambda x: 1 if x > 0 else 0)
    df["16_y_after_dob"] = df.dob + pd.to_timedelta(16 * 365,
                                                                  unit='d')

    new_joined_list = []
    for i, v in enumerate(list(df.joined)):
        if pd.isnull(v):
            new_joined_list.append(pd.to_datetime(df[["16_y_after_dob"]].iloc[i]["16_y_after_dob"]))
        else:
            new_joined_list.append(pd.to_datetime(v))

    df["joined"] = new_joined_list

    df = df.drop(columns=["16_y_after_dob"])

    df["seasons_with_club"] = df["fifa year"] - pd.DatetimeIndex(
        df.joined).year

    df["on_loan"] = df.loaned_from.map(lambda x: 0
                                                     if pd.isnull(x) else 1)

    df[
        "remaining_seasons_on_contract"] = df.contract_valid_until - df[
            "fifa year"]

    # Deleting additional not needed columns
    df = df.drop(columns=[
        'receiving_club',
        #'player_name',
        'position', 'giving_club',
        'transfer_movement', 'transfer_period', 'receiving_league', 'year',
        'season'
    ])

    df = df.drop(columns=[
    #"sofifa_id", "long_name",
    "dob", "joined", "nation_position",
    "nation_jersey_number", "loaned_from", "contract_valid_until"
    ])

    return df


def preprocessing(df):

    # Remove "+2" or similar from ratings columns
    position_cols = [
        'ls', 'st', 'rs', 'lw', 'lf', 'cf', 'rf', 'rw', 'lam', 'cam', 'ram',
        'lm', 'lcm', 'cm', 'rcm', 'rm', 'lwb', 'ldm', 'cdm', 'rdm', 'rwb',
        'lb', 'lcb', 'cb', 'rcb', 'rb'
    ]

    for pos in position_cols:
        df[pos] = df[pos].map(position_field_transform)

    return df


if __name__ == '__main__':

    # Define if with or without web scraping of sofifa IDs
    with_webscraping = input("Execute code with web scraping? (Y/n) ")
    if with_webscraping != "Y" and with_webscraping != "n":
        print("Invalid input. Restart!")

    # Load and clean input data
    path_to_transfer = input("Provide file path to transfer_history_combined file:  ")
    transfer_df = get_data(path_to_transfer)
    transfer_df = transfer_cleaning(transfer_df)

    path_to_player = input(
        "Provide file path to players_combined file:    ")
    players_df = get_data(path_to_player)
    players_df = players_cleaning(players_df)

    path_to_save = input("Provide file path to save final dataframe as csv (don't forget filename including .csv extenstion):   ")

    # Merge dataframe
    merged_df = merge_by_name_only(transfer_df, players_df)

    if with_webscraping=="Y":
        merged_2_df = merge_by_sofifa_id(add_sofifa_id_to_non_matched_transfers(transfer_df, players_df), players_df)

        merged_df = concat_datasets(merged_df, merged_2_df)

    master_df = clean_master_df(merged_df)

    master_df = preprocessing(master_df)

    master_df.to_csv(path_to_save, index_label=False)
    print(f"Master data frame saved under {path_to_save}")
