from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from market_value_predictor.data import get_data_from_gcp
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from termcolor import colored
import joblib
from market_value_predictor.gcp import storage_upload
from sklearn.metrics import r2_score, mean_absolute_error
import numpy as np
from market_value_predictor.utils import usable_columns


class Trainer:
    def __init__(self):
        self.numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
        pass

    def set_columns_lists(self, df):
        self.all_cats = list(df.select_dtypes(object).columns)

        self.all_numerics = list(df.select_dtypes(include=self.numerics).columns)

        self.all_numerics.remove("fee_cleaned")

        self.encoded_columns = (
            [elem for elem in self.all_numerics if "player_tags_" in elem]
            + [elem for elem in self.all_numerics if "player_positions_" in elem]
            + [elem for elem in self.all_numerics if "player_traits_" in elem]
        )

        self.all_numerics_wo_encoded = []
        for elem in self.all_numerics:
            if elem not in self.encoded_columns:
                self.all_numerics_wo_encoded.append(elem)

        self.numericals_zero_impute = [
            "gk_diving",
            "gk_handling",
            "gk_kicking",
            "gk_reflexes",
            "gk_positioning",
            ]

        self.numericals_mean_impute = []

        for elem in self.all_numerics_wo_encoded:
            if elem not in self.numericals_zero_impute:
                self.numericals_mean_impute.append(elem)

        return self

    def set_transformers(self):
        self.num_zero_tr = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
                ("scaler", StandardScaler()),
            ]
        )

        self.num_mean_tr = Pipeline(
            [("imputer", SimpleImputer(strategy="mean")),
            ("scaler", StandardScaler())]
        )

        self.cat_tr = Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="Other")),
            ("encoder", OneHotEncoder(handle_unknown="ignore"))
        ])

        return self

    def set_pipeline(self):
        preprocessor = ColumnTransformer(
            [
                (
                    "numerics_zero_imputing",
                    self.num_mean_tr,
                    self.numericals_zero_impute,
                ),
                (
                    "numerics_mean_imputing",
                    self.num_mean_tr,
                    self.numericals_mean_impute,
                ),
                ("cat_tr", self.cat_tr, self.all_cats),
            ],
            remainder="passthrough",
        )

        self.pipeline = Pipeline(
            [("preprocessing", preprocessor),
             ("regressor", XGBRegressor(
                 gamma=87,
                 learning_rate=0.2081503,
                 max_depth=2,
                 n_estimators=894,
                 n_jobs=-1,
                 reg_alpha=88,
                 reg_lambda=26
             ))]
        )

    def split_train_test(self, df):
        df_train, df_test = train_test_split(df, test_size=0.2)

        self.X_train = df_train.drop(columns="fee_cleaned")
        self.y_train = df_train["fee_cleaned"]
        self.X_test = df_test.drop(columns="fee_cleaned")
        self.y_test = df_test["fee_cleaned"]

    def run(self):
        self.pipeline.fit(self.X_train, self.y_train)

    def evaluate(self):
        y_pred = self.pipeline.predict(self.X_test)

        rmse = np.sqrt(((y_pred - self.y_test) ** 2).mean())
        r2 = r2_score(self.y_test, y_pred)
        mae = mean_absolute_error(self.y_test, y_pred)

        return round(rmse, 2), round(mae, 2), round(r2, 2)

    def save_model_locally(self):
        joblib.dump(self.pipeline, "model.joblib")
        print(colored("=> model.joblib saved locally", "green"))


if __name__ == "__main__":
    # get data form GCP storage
    df = get_data_from_gcp()
    df = df[usable_columns]

    # create Trainer object
    trainer = Trainer()

    # define lists of columns for pipeline
    trainer.set_columns_lists(df)

    # define transformers
    trainer.set_transformers()

    # set pipeline
    trainer.set_pipeline()

    # split dataset into train and test
    trainer.split_train_test(df)

    # train pipeline
    trainer.run()

    # evaluate model
    rmse, mae, r2 = trainer.evaluate()
    print(f"rmse: {rmse}")
    print(f"mae: {mae}")
    print(f"r2: {r2}\n")

    # save model locally
    trainer.save_model_locally()

    # upload model
    storage_upload()
    print(f"\nModel uploaded to GCP storage")
