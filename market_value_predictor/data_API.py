# IMPORTS ---------------------
from collections import UserList
import pandas as pd
import requests
from bs4 import BeautifulSoup



# DATA RELATED FUNCTIONS ------
def get_data(filepath):
    '''
    Load the csv file from the raw_data directory
    '''
    df = pd.read_csv(filepath)
    return df


def get_data2(filepath):
    '''
    Load the csv file from the raw_data directory
    '''
    df = pd.read_csv(filepath)
    return df

### API: get_data does not work when the notebook is not in the right place. Path is static at "../raw_data/" ###


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
    df.sort_values(["year", "player_name", "fee_cleaned"],
                          ascending=(True, True, False),
                          inplace=True)

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

    for idx, name in enumerate(df[column_name]):
        params = {
            'keyword': name
        }
        response = requests.get(URL, params=params)
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            sofifa_ids = soup.find_all("img", class_="player-check")
            if len(sofifa_ids) != 1:
                df['sofifa_id'][idx] = 'Nan'
            else:
                df['sofifa_id'][idx] = sofifa_ids[0].get('id')
        except AttributeError:
            df['sofifa_id'][idx] = 'Nan'

    df.to_csv('../raw_data/scrapped_id.csv')

    return 'CSV generated'

### API: Misses the functionality to only look up those players that have not
### been matched via name, currently all names would be inserted into web scraper
### which is quite expensive

def text_preprocessing(df):
    '''
    processes the text of the dataframe to lowercase and remove accents
    from the players names
    '''
    df["player_name"] = df["player_name"].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    df.drop(df.filter(regex="Unname"), axis=1, inplace=True)
    return df




def generate_dataset1():
    '''
    joins the player features dataframe with the transfer history dataframe
    via a player name and the fifa year
    '''

    # generate dataframe for player features
    features_df = pd.read_csv(PATH + 'players_combined.csv')

    # FEATURE ENG.1 : generate last name column from short name
    features_df["last_name"] =+ features_df["short_name"].str.extract(r'\b(\w+)$', expand=True)

    # FEATURE ENG.2 : adding a first name column
    splited_name = features_df['long_name'].str.split(' ', 1)
    f_name = []
    first_names = []
    for _, value in splited_name.items():
        f_name.append(value)
    for i in range(len(f_name)):
        first_names.append(f_name[i][0])
    # create a datframe out of the first names
    fname_df = pd.DataFrame(first_names, columns=['first_name'])

    # concatenate the fname_df to the features_df
    features_df = pd.concat([features_df, fname_df], axis=1, sort=False)
    # concatenate a column with player first & last name
    features_df["player_name"] = features_df["first_name"] + " " + features_df["last_name"]

    # process the player_name to lower case and no accents
    features_df = text_preprocessing(features_df)

    # generate the transfer history dataframe since 2015
    transfer_df = get_data('transfer_history_combined.csv')
    transfer_df = transfer_history_cleaning(transfer_df, 2014)

    #import ipdb; ipdb.set_trace()
    # merging datasets by player name and FIFA year
    merged_df = transfer_df.merge(features_df, on=["player_name", "fifa year"], how='inner')

    #merged_df.to_csv('../raw_data/transfer_features_by_name.csv')
    return merged_df


def generate_dataset2():
    '''
    joins the scrapped_id datframe with the transfer history dataframe
    '''

    # getting the scrapped_id_dataframe
    scrapped_df = get_data('scrapped_id.csv')
    scrapped_df = scrapped_df.drop_duplicates(subset=['sofifa_id'])
    # convert names to string
    scrapped_df["name"] = scrapped_df["name"].astype("string")
    # removing all the nan values
    scrapped_df = scrapped_df[scrapped_df["sofifa_id"] != "Nan"]
    # converting id's to int
    scrapped_df["sofifa_id"] = scrapped_df["sofifa_id"].astype("int64")
    # rename name column
    scrapped_df =scrapped_df.rename(columns={'name': 'player_name'})
    scrapped_df = text_preprocessing(scrapped_df)


    # getting the transfer history dataframe
    transfer_df = get_data('transfer_history_combined.csv')
    transfer_df = transfer_history_cleaning(transfer_df, 2014)
    # merging scrapped_id_df with transfer_df by the name so as to add the sofifa_id to
    # the transfer_df
    transfer_df = transfer_df.merge(scrapped_df, on=["player_name"], how='inner')

    features_df = get_data('players_combined.csv')

    merged_df = transfer_df.merge(features_df, on=["sofifa_id", "fifa year"], how='inner')

    merged_df.to_csv('../raw_data/transfer_features_by_id.csv')

    return 'CSV created'



def join_everything():
    '''joins all dataframes together'''

    # this wil create transfer_features_by_id && transfer_features_by_name
    generate_dataset1()
    generate_dataset2()

    df_byname = get_data('transfer_features_by_name.csv')
    df_byid = get_data('transfer_features_by_id.csv')

    df_byname.drop('first_name', axis=1, inplace=True)
    df_byname.drop('last_name', axis=1, inplace=True)
    df_byname.drop('age_y', axis=1, inplace=True)

    df_byid.drop('age_y', axis=1, inplace=True)
    df_byid.drop(columns=["Unnamed: 0.1"], inplace=True)


    # final dataset
    data = pd.concat([df_byid, df_byname],axis="index",sort=False)
    data = data.drop_duplicates(keep="first")

    data.to_csv('../raw_data/data.csv')
    return 'CSV file created'


if __name__ == '__main__':
    transfer_df = get_data("raw_data/transfer_history_combined.csv")
