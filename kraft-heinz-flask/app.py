# region Set up of Flask
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
import os
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

import numpy as np
from pickle import load
import config
from bench import FeatureInstance as FI
import pandas as pd
import xgboost as xgb
import json
from sklearn.metrics import mean_absolute_error
from tensorflow import keras

# Init app

app = Flask(__name__)

# endregion

# region Set up of Database

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)
# endregion

# region Set up of database models

# endregion

# region Set up of routes

CORS(app, resources={r"/api": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
# endregion

# region Set up API
data_path_line = 'data/original-format/line-stats/'
file_name = 'AI_Hourly_2021.xlsx'

df = pd.read_excel(os.path.join(data_path_line, file_name), )

feature_instances_fetched = {
    '1': FI(training=True,
            granular=False,
            on=config.AI_id,
            line="Line 1",
            estimator_params=config.estimator_params).fetch(testing_only=True)["XYdates_test"],
    # '2': FI(training=True,
    #       granular=False,
    #       on=config.AI_id,
    #       line="Line 3",
    #       estimator_params=config.estimator_params).fetch(testing_only=True)["XYdates_test"],
    # '3': FI(training=True,
    #        granular=False,
    #        on=config.AI_id,
    #        line="Line 4",
    #        estimator_params=config.estimator_params).fetch(testing_only=True)["XYdates_test"]
}


@app.route('/api/cases_overfill/<line>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_cases_overfill(line):
    if config.CURRENT_MODEL_TYPE == "lstm":
        # Neural net
        model = keras.models.load_model(
            os.path.join(config.MODELS_PATH, "keras"))
    else:
        # XGBoost
        model = load(open(os.path.join(config.MODELS_PATH,
                                       config.MODEL_NAMES["Line 1"]),
                          "rb"))

    dates = feature_instances_fetched[line][2]
    current_date_idx = list(dates).index(config.CURRENT_DATE)
    offset_idx = 0
    dates = dates[offset_idx:current_date_idx + 2]
    Y_true = feature_instances_fetched[line][0][offset_idx:current_date_idx + 1]

    X_test = feature_instances_fetched[line][1].iloc[offset_idx:current_date_idx + 1, :]
    X_test = extract_input(config.estimator_params, X_test)
    Y_pred = model.predict(X_test)
    Y_pred = Y_pred.flatten()

    X_next = feature_instances_fetched[line][1].iloc[[current_date_idx + 1]]
    X_next = extract_input(config.estimator_params, X_next)

    Y_pred_next = model.predict(X_next)
    date_next = dates.tolist()[-1]

    mAE = mean_absolute_error(Y_true, Y_pred)

    return_object = {
        "Actual": Y_true.values.tolist(),
        "Predicted": Y_pred.tolist(),
        "Dates": dates[:-1].tolist(),
        "Next prediction": json.dumps(Y_pred_next[0].item()),
        "Next date": date_next,
        'mAE': mAE
    }

    return jsonify(return_object)


def extract_input(preprocessing_params, X):
    relevant_vars_HW = preprocessing_params["relevant_vars_HW"]
    if "Date" in relevant_vars_HW:
        relevant_vars_HW.remove("Date")

    ai_input = X[relevant_vars_HW]

    cw_input_cols = []
    CW_cols = preprocessing_params["input_lag_columns"]
    cw_input_cols.extend(CW_cols)
    lag_cw = preprocessing_params["input_lag_cw"]
    for lag in range(1, lag_cw):
        for CW_col in CW_cols:
            cw_input_cols.append(f"{CW_col}_{lag}")

    cw_input = X[cw_input_cols].values
    cw_input = np.reshape(
        cw_input, (cw_input.shape[0], len(CW_cols), lag_cw))

    year_input = X["year"]
    shift_input = X["Shift"]
    dow_input = X["day of week"]
    hour_input = X["hour"]

    return [ai_input.values, cw_input, year_input, shift_input, dow_input, hour_input]


def get_2_values_in_time(df, start_date, end_date, line='Line 1', col1='Cases Produced', col2='Target'):
    line_name = 'Line ' + str(line)
    df = df[df['Line'] == line_name]
    df = df[[col1, col2, 'Date']]
    df['Date'] = pd.to_datetime(df['Date'])

    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    dic_df = dict()
    dic_df[col1] = list(df[col1])
    dic_df[col2] = list(df[col2])
    dic_df['Date'] = list(df['Date'])

    return dic_df


def get_values_in_time(df, start_date, end_date, line='Line 1', col1='Cases Produced', col2='Target'):
    line_name = 'Line ' + str(line)
    df = df[df['Line'] == line_name]
    df = df[[col1, col2, 'Date']]
    df['Date'] = pd.to_datetime(df['Date'])

    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    dic_df = dict()
    dic_df[col1] = list(df[col1])
    dic_df[col2] = list(df[col2])
    dic_df['Date'] = list(df['Date'])

    return dic_df


def get_value_in_time(df, start_date, end_date, line='Line 1', col='SKU'):

    line_name = 'Line ' + str(line)
    df = df[df['Line'] == line_name]
    df = df[[col, 'Date']]
    df['Date'] = pd.to_datetime(df['Date'])

    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    dic_df = dict()
    dic_df[col] = list(df[col])
    dic_df['Date'] = list(df['Date'])

    return dic_df


@app.route('/api/target_actual_cases/<start>/<end>/<line>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_target_actual_cases(start, end, line):

    return_object = get_values_in_time(df, start, end, line=line)

    return jsonify(return_object)


@app.route('/api/sku/<start>/<end>/<line>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_sku(start, end, line):

    return_object = get_value_in_time(
        df=df, start_date=start, end_date=end, line=line, col='SKU')

    return jsonify(return_object)


# region Start the app
if __name__ == '__main__':
    app.run(debug=True)
# endregion
