import pandas as pd
# import numpy as np
import os
import config as cn
import file_manager_helper as fmh
from typing import Optional
from math import floor
# from sklearn.preprocessing import MinMaxScaler


class FeatureInstance:
    """
    Feature instance generator.
    Fetches and manipulates data sources according to needs.

    Attributes
    ----------
    training: bool
        Specifies if estimator_params should be looked at which would contain shaping params
    granular: bool
        Whether to  keep it as granular as possible
        (True corresponds to grouping by both SKU and dates on AI data and not flooring CW dates)
    on: str
        Which dataset's shape to retain (if on CW data, granular must be True)
    line: str
        Line Feature Instance to fetch.

    Methods
    -------
    get_check_weigher :
        Returns dataframe of check-weigher data only.
    get_hourly_stats :
        Returns dataframe of AI hourly data only.
        Assigns and initializes the relevant parameters in the model design process.
    fetch :
        Fetches combined sources according to settings.
    """

    def __init__(self,
                 training: bool,
                 granular: bool,
                 quarterly: bool,
                 on: str,
                 line: str, estimator_params: Optional[dict] = None):

        self.training = training
        self.granular = granular
        self.line = line
        self.on = on
        self.estimator_params = estimator_params
        self.quarterly = quarterly

    def get_check_weigher(self):
        print("Get check weigher")
        # Get files and available lines
        files = os.listdir(cn.COMBINED_GRANULAR_DATA_PATH)
        lines = [fn.split("_")[0] for fn in files]

        # Read correct file
        df_check = pd.read_csv(os.path.join(
            cn.COMBINED_GRANULAR_DATA_PATH, files[lines.index(self.line.split(" ")[1])]))
        df_check[cn.DATE_COL] = pd.to_datetime(df_check[cn.DATE_COL])

        # Switching overfilled label to represent 1 as overfilled
        overfilled = [1 if i == 0 else 0 for i in df_check[cn.CW_REJECTS_COL]]
        df_check[cn.CW_REJECTS_COL] = overfilled

        if not self.granular:
            if self.quarterly:
                df_check[cn.DATE_COL] = df_check[cn.DATE_COL].dt.round('15min')
                aggregates = prepare_aggregates(cn.OVERFILL_AGGREGATION_TYPES)
                df_check_overfills = df_check.groupby(cn.DATE_COL)["Overfill"].agg(aggregates)
                df_check = df_check.groupby(cn.DATE_COL).sum().reset_index()
                df_check.drop(["Unnamed: 0", "Overfill"], axis=1, inplace=True)
                df_check[list(cn.OVERFILL_AGGREGATION_TYPES.keys())] = df_check_overfills[list(cn.OVERFILL_AGGREGATION_TYPES.keys())].values
                df_check["Absolute Overfill"] = abs(df_check["Underfill"]) + df_check["Overfill"]
            else:
                df_check[cn.DATE_COL] = df_check[cn.DATE_COL].dt.floor(freq="H")
                aggregates = prepare_aggregates(cn.OVERFILL_AGGREGATION_TYPES)
                df_check_overfills = df_check.groupby(cn.DATE_COL)["Overfill"].agg(aggregates)
                df_check = df_check.groupby(cn.DATE_COL).sum().reset_index()
                df_check.drop(["Unnamed: 0", "Overfill"], axis=1, inplace=True)
                df_check[list(cn.OVERFILL_AGGREGATION_TYPES.keys())] = df_check_overfills[list(cn.OVERFILL_AGGREGATION_TYPES.keys())].values
                df_check["Absolute Overfill"] = abs(df_check["Underfill"]) + df_check["Overfill"]
        return df_check

    def get_hourly_stats(self):
        print("Get hourly stats")
        # Get hourly data for specific line
        df = fmh.get_hourly(self.line, cn.HOURLY_LINESTATS_DATA_PATH)
        df[cn.DATE_COL] = pd.to_datetime(df[cn.DATE_COL])

        if self.granular:
            group = cn.DATE_COL
        else:
            group = cn.DATE_COL

        df["SKU"] = [s.rstrip("\n") for s in df["SKU"]]
        return df

    def get_quarterhourly_stats(self):
        print("Get quarterhourly stats")

        df = fmh.get_quarter_hourly(self.line, cn.QUARTER_HOURLY_LINESTATS_DATA_PATH)
        df[cn.DATE_COL] = pd.to_datetime(df[cn.DATE_COL])

        if self.granular:
            group = cn.DATE_COL
        else:
            group = cn.DATE_COL

        df["SKU"] = [s.rstrip("\n") for s in df["SKU"]]
        return df

    def fetch(self, testing_only: bool):
        if self.quarterly:
            ai = self.get_quarterhourly_stats()
        else:
            ai = self.get_hourly_stats()

        cw = self.get_check_weigher()

        if not self.training:

            if self.on == cn.AI_id:
                df = pd.merge(ai, cw, on=cn.DATE_COL).dropna()

            elif self.on == cn.CW_id:

                assert self.granular == True, "No sense in matching on CW if CW is aggregated by hour."
                cw[f"{cn.DATE_COL}_temp"] = cw[cn.DATE_COL].dt.floor(freq="H")
                df = pd.merge(ai, cw,
                              left_on=cn.DATE_COL,
                              right_on=f"{cn.DATE_COL}_temp",
                              how="inner").dropna()
                df.drop([f"{cn.DATE_COL}_temp", f"{cn.DATE_COL}_x"],
                        axis=1, inplace=True)

            else:
                raise ValueError("Unavailable dataset tag suggested.")
        # In case feature instance is used for training
        else:
            estimator_params = self.estimator_params
            input_lag_columns = estimator_params["input_lag_columns"] if "input_lag_columns" in estimator_params else None
            input_lag_cw = estimator_params["input_lag_cw"] if "input_lag_cw" in estimator_params else None
            hot_encode_columns = estimator_params["hot_encode_columns"] if "hot_encode_columns" in estimator_params else None
            scaling = estimator_params["scaling"] if "scaling" in estimator_params else None
            input_temporal_granularities = estimator_params["input_temporal_granularities"]
            train_mass = estimator_params["train_mass"]
            test_mass = estimator_params["test_mass"]
            label = estimator_params["label"]
            label_mold = estimator_params["label_mold"]
            label_window = estimator_params["label_window"]
            relevant_vars_HW = estimator_params["relevant_vars_HW"]

            if self.on == cn.AI_id:
                hourly = ai[relevant_vars_HW]

                # Initializing merged df
                df = pd.merge(hourly, cw, on=cn.DATE_COL).dropna()

                # Setting input lags
                if input_lag_columns != None:
                    for column in input_lag_columns:
                        for lag in range(1, input_lag_cw):
                            df[f"{column}_{lag}"] = df[column].shift(lag)

                # Scaling
                if scaling != None:
                    if scaling == "min_max":
                        scaler = MinMaxScaler(feature_range=(0, 1))
                        df = pd.DataFrame(scaler.fit_transform(df))
                    else:
                        raise NotImplementedError(
                            "MinMax scaling is the only one implemented at the moment.")

                # Hot encoding relevant variables
                if hot_encode_columns != None:
                    df = pd.get_dummies(data=df, columns=hot_encode_columns)

                # Preparing label
                if label_mold == "cummulative":
                    # df["Label"] = df[label].shift(-label_window).rolling(label_window, min_periods=1).sum().dropna()
                    # df["Label"] = df[label].shift(-1).rolling(label_window, min_periods=1).sum().dropna()
                    df["Label"] = df[label].shift(-1).rolling(
                        label_window, min_periods=1).sum()
                    df.dropna(inplace=True)
                elif label_mold == "point":
                    raise NotImplementedError(
                        "Predicting a point is deemed not useful rn.")

                # Adding temporal features and removing datetime series from the dataframe
                for datetime_type in input_temporal_granularities:
                    df[datetime_type] = dt_mapper(
                        df[cn.DATE_COL], datetime_type)

                dates = df[cn.DATE_COL]
                df = df.drop([cn.DATE_COL], axis=1)

                assert (
                    train_mass + test_mass) == 10, "Train and test split is not consistent."

                cutoff_point = floor(df.shape[0] * (train_mass/10))
                dates_train = dates[:cutoff_point]
                dates_test = dates[cutoff_point:]
                dates_train.reset_index(drop=True, inplace=True)
                dates_test.reset_index(drop=True, inplace=True)
                X_Y_train = df.iloc[:cutoff_point, :]
                X_Y_test = df.iloc[cutoff_point:, :]

                # Separating labels from features
                Y_train = X_Y_train['Label']
                X_train = X_Y_train.drop('Label', axis=1)

                Y_test = X_Y_test['Label']
                X_test = X_Y_test.drop('Label', axis=1)

                if testing_only:
                    df = {
                        "XYdates_test": [Y_test, X_test, dates_test]
                    }
                else:
                    df = {
                        "XYdates_train": [Y_train, X_train, dates_train],
                        "XYdates_test": [Y_test, X_test, dates_test]
                    }

            elif self.on == cn.CW_id:
                raise ValueError(
                    "Currently no feature preprocessing is implemented for CW data granularity.")

        return df


# TODO: Wrap into lambda function for mapping feature as a placeholder, instead of
# explicitly storing it into a dictionary for every possible choice.
def dt_mapper(feature, temporal_granularity):
    dt_mapper = {
        "hour": feature.dt.hour,
        "day of week": feature.dt.weekday,
        "week": feature.dt.isocalendar().week,
        "month": feature.dt.month,
        "year": feature.dt.year
    }
    return dt_mapper[temporal_granularity]

def prepare_aggregates(*args):
    aggregates = []

    for agg in args:
        for type, func in agg.items():
            aggregates.append((type, func))

    return aggregates



estimator_params = {
    "input_lag_columns": ["Unit Weight", "Overfill", "Weight Result"],
    "input_lag_cw": 6,
    "relevant_vars_HW": ["Date", "Shift", "Cases Produced",
                         "Performance", "Availability", "Quality",
                         "Average Speed", "Backed Up (min)", "DT Events"],

    "input_temporal_granularities": ["day of week", "hour"],  # "year"
    "hot_encode_columns": ["Shift"],  # "year"
    # "scaling": "min_max",

    # Following two variables must sum up to 10
    "train_mass": 9,
    "test_mass": 1,

    "label_window": 3,
    "label": "Overfill",  # Could also be Weight_Result
    "label_mold": "cummulative",  # Could also be point
}

# FI = FeatureInstance(
#     training=False,
#     granular=False,
#     on=cn.AI_id,
#     line="Line 1",
#     quarterly=False,
#     estimator_params=estimator_params
# )

# df = FI.fetch(testing_only=False)
