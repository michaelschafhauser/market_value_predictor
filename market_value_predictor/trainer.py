from market_value_predictor.data import get_data, id_scrapping, transfer_cleaning
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class Trainer:
    def __init__(self):
        pass

    def set_pipeline(self):
        '''defines the pipeline as a class attribute'''
        pass

if __name__ == '__main__':
    # getting the data
    df = get_data('baseline_df.csv')
    # cleaning the data (do we need to clean the data at this stage?)

    # split data
    X = df.drop(columns=['fee_cleaned'])
    y = df['fee_cleaned']
    # train model
    # evaluate
    # save model
    pass
