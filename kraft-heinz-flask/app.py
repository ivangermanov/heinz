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
import keras

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


# class Todo(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100))
#     description = db.Column(db.String(400))

#     def __init__(self, title, description):
#         # Add the data to the instance
#         self.title = title
#         self.description = description


# class TodoSchema(ma.Schema):
#     class Meta:
#         fields = ('id', 'title', 'description')


# todo_schema = TodoSchema()
# todos_schema = TodoSchema(many=True)
# endregion

# region Set up of routes

CORS(app, resources={r"/api": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
# endregion

# region Set up API


# @app.route('/api/todo', methods=['POST'])
# @cross_origin(origin='*', headers=['content-type'])
# def add_todo():
#     # get the data
#     title = request.json['title']
#     description = request.json['description']

#     # Create an instance
#     new_todo = Todo(title, description)

#     # Save the todo in the db
#     db.session.add(new_todo)
#     db.session.commit()

# # return the created todo
#     return todo_schema.jsonify(new_todo)

# Get all todos

data_path_line = 'data/original-format/line-stats/'
file_name = 'AI_Hourly_2021.csv'

df = pd.read_csv(os.path.join(data_path_line, file_name))


def lazy_fetch():
    lazy_to_fetch = dict()
    for l in range(1, config.LINE_COUNT):
        print("Lazy fetch:", l)
        if l not in config.LINES_INCOMPLETE:
            line_tag = f"Line {l}"
            lazy_to_fetch[line_tag] = FI(training=True,
                                         granular=False,
                                         on=config.AI_id,
                                         line=line_tag,
                                         estimator_params=config.estimator_params).fetch(testing_only=True)["XYdates_test"]

    return lazy_to_fetch


lazy_fetched = lazy_fetch()


@app.route('/api/cases_overfill/<line>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_cases_overfill(line):
    if config.CURRENT_MODEL_TYPE == "lstm":
        model = keras.models.load_model(os.path.join(
            config.MODELS_PATH, f"Line {str(line)}"))
    else:
        model = load(open(os.path.join(config.MODELS_PATH,
                                       config.MODEL_NAMES["Line 1"]),
                          "rb"))

    dates = lazy_fetched[f"Line {line}"][2]
    current_date_idx = list(dates).index(config.CURRENT_DATE)
    # offset_idx = current_date_idx-config.N_TENDENCY
    offset_idx = 0
    dates = dates[offset_idx:current_date_idx + 2]
    Y_true = lazy_fetched[f"Line {line}"][0][offset_idx:current_date_idx + 1]

    X_test = lazy_fetched[f"Line {line}"][1].iloc[offset_idx:current_date_idx + 1, :]
    X_test = extract_input(config.estimator_params, X_test)

    Y_pred = model.predict(X_test)
    Y_pred = Y_pred.flatten()

    X_next = lazy_fetched[f"Line {line}"][1].iloc[[current_date_idx + 1]]
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
    cw_input = np.reshape(cw_input, (cw_input.shape[0], len(CW_cols), lag_cw))

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


def get_value_in_time(df, start_date, end_date, line='Line 1', col='SKU'):

    line_name = 'Line ' + str(line)
    df = df[df['Line'] == line_name]
    df = df[[col, 'Date']]
    df['Date'] = pd.to_datetime(df['Date'])

    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    # print(df)
    dic_df = dict()
    dic_df[col] = list(df[col])
    dic_df['Date'] = list(df['Date'])

    return dic_df


@app.route('/api/target_actual_cases/<start>/<end>/<line>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_target_actual_cases(start, end, line):

    return_object = get_2_values_in_time(
        df=df, start_date=start, end_date=end, line=line)

    return jsonify(return_object)


@app.route('/api/sku/<start>/<end>/<line>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_sku(start, end, line):

    return_object = get_value_in_time(
        df=df, start_date=start, end_date=end, line=line, col='SKU')

    return jsonify(return_object)


@app.route('/api/cases_produced/<start>/<end>/<line>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_cases_produced(start, end, line):

    return_object = get_value_in_time(
        df=df, start_date=start, end_date=end, line=line, col='Cases Produced')

    return jsonify(return_object)


def get_all_skus_as_list():
    skus = set()
    for line in range(1, config.LINE_COUNT):
        if line not in config.LINES_INCOMPLETE:
            df = pd.read_csv(
                f"data/preprocessed_format/hourly_perline/Line_{line}.csv")
            skus.update(df["SKU"])
    return list(skus)


@app.route('/api/get_all_skus', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_all_skus():
    return jsonify(get_all_skus_as_list())


@app.route('/api/sku_overfill_heat/<sku>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_sku_overfill_heat(sku):

    return_object = {}
    return_object["Lines"] = {}
    return_object["Date"] = {}
    data = []

    line_counter = 0
    date_counter = 0
    max_overfill = float("-inf")
    min_overfill = float("inf")

    line_counter = 0
    date_counter = 0
    max_overfill = float("-inf")
    min_overfill = float("inf")

    for line in range(1, config.LINE_COUNT):
        if line not in config.LINES_INCOMPLETE:
            df = pd.read_csv(
                f'data/preprocessed_format/hourly_perline/Line_{line}.csv')

            df["Date"] = pd.to_datetime(df["Date"])
            if sku in list(df["SKU"]):
                if line not in return_object["Lines"]:
                    return_object["Lines"][line] = line_counter
                    line_counter += 1

                df = df[df["SKU"] == sku]

                # Adding data in following format [[x-coord-idx1, y-coord-idx1, overfill-value1], [x-coord-idx2, y-coord-idx2, overfill-value2], ...]
                data_temp = [[date, return_object["Lines"][line], overfill_v] for (
                    overfill_v, date) in zip(df["Overfill"], df["Date"])]

                data.extend(data_temp)
                max_for_line = max(df["Overfill"])
                min_for_line = min(df["Overfill"])

                if max_overfill < max_for_line:
                    max_overfill = max_for_line
                if min_overfill > min_for_line:
                    min_overfill = min_for_line

    data = sorted(data)

    for dp in data:
        if dp[0] not in return_object["Date"].keys():
            return_object["Date"][dp[0]] = date_counter
            date_counter += 1
        dp[0] = return_object["Date"][dp[0]]

    return_object["data"] = data
    return_object["Date"] = list(return_object["Date"].keys())
    return_object["Lines"] = list(return_object["Lines"].keys())
    return_object["min_colorcode"] = min_overfill
    return_object["max_colorcode"] = max_overfill

    return jsonify(return_object)


@app.route('/api/pcp/<line>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_pcp(line):
    return_object = {}
    dimensions = ["Shift", "Cases Produced", "Weight Result",
                  "Uptime (min)", "Stops", "Overfill", "OEE", "Average Speed"]
    df = pd.read_csv(
        'data//preprocessed_format/hourly_perline/Line_{line}.csv')
    df = df[dimensions]

    return_object["columns"] = dimensions
    return jsonify(return_object)

# Get a single todo

# @app.route('/api/get_prediction', methods=['GET'])
# @cross_origin(origin='*', headers=['Content-Type'])
# def get_prediction():
#     model = load(open(os.path.join(config.MODELS_PATH,
#                                    config.MODEL_NAMES["Line 1"]),
#                                    "rb"))

#     # TODO: Refactor for dummy_deploy functionality
#     feature_instance = FI(training = True,
#                           granular=False,
#                           on=config.AI_id,
#                           line = "Line 1",
#                           estimator_params=config.estimator_params,
#                           dummy_deploy=False)

#     testing_data = feature_instance.fetch()["XYdates_test"]
#     dates = testing_data[2]
#     current_date_idx = list(dates).index(config.CURRENT_DATE)
#     dates = dates[:current_date_idx + 2]
#     Y_true = testing_data[0][:current_date_idx + 1]

#     X_test = testing_data[1].iloc[:current_date_idx + 1, :]
#     Y_pred = model.predict(X_test)

#     X_next = X_test.iloc[current_date_idx + 1, :]
#     Y_pred_next = model.predict(X_next)
#     date_next = dates[-1]

#     return_object = {
#         "True labels": Y_true,
#         "Predicted labels": Y_pred,
#         "Dates": dates[:-1],
#         "Next prediction": Y_pred_next,
#         "Next date": date_next
#     }

#     return jsonify(return_object)


# @app.route('/api/todo/<id>', methods=['PUT'])
# @cross_origin(origin='*', headers=['Content-Type'])
# def update_todo(id):
#     # get the todo first
#     todo = Todo.query.get(id)
#     # get the data
#     title = request.json['title']
#     description = request.json['description']

#     # set the data
#     todo.title = title
#     todo.description = description

#     # commit to the database
#     db.session.commit()

#     # return the new todo as per the schema
#     return todo_schema.jsonify(todo)

# # Delete a todo


# @app.route('/api/todo/<id>', methods=['DELETE'])
# @cross_origin(origin='*', headers=['Content-Type'])
# def delete_todo(id):
#     # get the todo to be deleted
#     todo = Todo.query.get(id)

#     # delete from the database
#     db.session.delete(todo)

#     # commit on the database
#     db.session.commit()

#     # return thr deleted todo as per the schema
#     return todo_schema.jsonify(todo)


# endregion

# region Start the app
if __name__ == '__main__':
    app.run(debug=True)
# endregion
