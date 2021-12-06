### DATA & MODEL LOCATIONS  - - - - - - - - - - - - - - - - - - -

PATH_TO_LOCAL_MODEL = 'model.joblib'


### GCP Storage - - - - - - - - - - - - - - - - - - - - - -

BUCKET_NAME = 'market_value_predictor'

##### Data  - - - - - - - - - - - - - - - - - - - - - - - -

# train data file location

BUCKET_TRAIN_DATA_PATH = 'data/master_df_with_webscraping.csv'

##### Model - - - - - - - - - - - - - - - - - - - - - - - -

# model folder name (will contain the folders for all trained model versions)
MODEL_NAME = 'predictor'

# model version folder name (where the trained model.joblib file will be stored)
MODEL_VERSION = 'v1'
