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
import datetime

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

# df = pd.read_csv(os.path.join(data_path_line, file_name))


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
                                         estimator_params=config.estimator_params,
                                         quarterly=False).fetch(testing_only=True)["XYdates_test"]

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


def get_2_values_in_time(start_date, end_date, line='1', col1='Cases Produced', col2='Target'):
    df = pd.read_csv(
        f"data/preprocessed_format/hourly_perline/Line_{line}.csv")
    line_name = 'Line ' + str(line)
    df = df[df['Line'] == line_name]
    df = df[[col1, col2, 'Date']]
    df['Date'] = pd.to_datetime(df['Date'])

    df = df[(df['Date'] >= datetime.datetime.strptime(start_date, "%d-%m-%Y"))
            & (df['Date'] <= datetime.datetime.strptime(end_date, "%d-%m-%Y"))]

    dic_df = dict()
    dic_df[col1] = list(df[col1])
    dic_df[col2] = list(df[col2])
    dic_df['Date'] = list(df['Date'])

    return dic_df


def get_value_in_time(start_date, end_date, line='1', col='SKU'):
    df = pd.read_csv(
        f"data/preprocessed_format/hourly_perline/Line_{line}.csv")
    line_name = 'Line ' + str(line)
    df = df[df['Line'] == line_name]
    df = df[[col, 'Date']]
    df['Date'] = pd.to_datetime(df['Date'])

    df = df[(df['Date'] >= datetime.datetime.strptime(start_date, "%d-%m-%Y"))
            & (df['Date'] <= datetime.datetime.strptime(end_date, "%d-%m-%Y"))]
    dic_df = dict()
    dic_df[col] = list(df[col])
    dic_df['Date'] = list(df['Date'])

    return dic_df


def get_average_speed_cases_hourly(begin_date, end_date, line, quarterly, overfill_col):
    quarterly = quarterly == "true"

    if quarterly:
        df = pd.read_csv(
            f"data/preprocessed_format/quarterhourly_perline/Line_{line}.csv")
    else:
        df = pd.read_csv(
            f"data/preprocessed_format/hourly_perline/Line_{line}.csv")

    df['Date'] = pd.to_datetime(df['Date'])
    df_l = df[(df["Date"] >= datetime.datetime.strptime(begin_date, "%d-%m-%Y"))
              & (df["Date"] <= datetime.datetime.strptime(end_date, "%d-%m-%Y"))]
    df_g = df_l[['Cases Produced', 'Rejects', overfill_col]].groupby(pd.cut(
        df_l["Average Speed"], np.arange(0, 115, 5))).sum()  # 5000 because of max, doesn't matter anyways
    df_g_col = df_l[['Cases Produced', 'Rejects', overfill_col]].groupby(
        pd.cut(df_l["Average Speed"], np.arange(0, 115, 5))).size()
    df_g['Amount of hours run on this Average Speed'] = df_g_col

    output = dict()
    # x-axis is average speed in agg bins, it is 110 instead of 115 because cut function returns one value less
    output['x_axis'] = np.arange(0, 110, 5).tolist()

    # y-axis contains all of the data we have on check-weigher
    # choose one of the 2
    # 1
    output['y_axis_cases_produced'] = list(df_g['Cases Produced'])
    output['y_axis_number_of_rejected_cases'] = list(df_g['Rejects'])

    # 2
    output['y_axis_overfill'] = list(df_g[overfill_col])

    # and on 2nd y axis we have:
    # hours spend on this setting (which is not true due to aggregation but lets ignore that)
    output['y_axis_time_spend'] = list(
        df_g['Amount of hours run on this Average Speed'])

    return output


def count_weight_result(row):
    if row['Weight Result'] == 0:
        return 30
    else:
        return 1


def get_average_speed_cases_check_weigher(begin_date, end_date, line, quarterly, overfill_col):
    quarterly = quarterly == "true"

    if quarterly:
        df = pd.read_csv(
            f"data/preprocessed_format/quarterhourly_perline/Line_{line}.csv")
    else:
        df = pd.read_csv(
            f"data/preprocessed_format/hourly_perline/Line_{line}.csv")

    df['Date'] = pd.to_datetime(df['Date'])
    df_l = df[(df["Date"] >= datetime.datetime.strptime(begin_date, "%d-%m-%Y"))
              & (df["Date"] <= datetime.datetime.strptime(end_date, "%d-%m-%Y"))]
    df_l['Weight Result size'] = df_l.apply(
        lambda row: count_weight_result(row), axis=1)
    df_g = df_l[['Weight Result size', 'Weight Result', overfill_col]].groupby(pd.cut(
        df_l["Average Speed"], np.arange(0, 115, 5))).sum()  # 5000 because of max, doesn't matter anyways
    df_g_col = df_l[['Weight Result size', 'Weight Result', overfill_col]].groupby(
        pd.cut(df_l["Average Speed"], np.arange(0, 115, 5))).size()
    df_g['Amount of hours run on this Average Speed'] = df_g_col

    output = dict()
    # x-axis is average speed in agg bins, it is 110 instead of 115 because cut function returns one value less
    output['x_axis'] = np.arange(0, 110, 5).tolist()

    # y-axis contains all of the data we have on check-weigher
    # choose one of the 2
    # 1
    output['y_axis_cases_produced'] = list(df_g['Weight Result size'])
    output['y_axis_amount_of_overfill_cases'] = list(df_g['Weight Result'])

    # 2
    output['y_axis_overfill'] = list(df_g[overfill_col])

    # and on 2nd y axis we have:
    # hours spend on this setting (which is not true due to aggregation but lets ignore that)
    output['y_axis_time_spend'] = list(
        df_g['Amount of hours run on this Average Speed'])

    return output


def full_sku(row):
    return str(row['index']) + ' - ' + str(row[4])


def adjust_sku(df):
    change_dict = {
        '10162 - 6 OZ OM NATURAL SALAMI 8 CT': '10162 - Nat Salami',
        '9630 - 8Z OM D F TKY CRD BK PEP 8': '9630 - 8Z Cracked Black Pepper Turkey',
        '9645 - 8Z OM DL SHVD TKY BRST LS SMKD 8CT': '9645 - 8Z OM DL SHVD TKY BRST LS SMKD 8CT\t',
        '7353 - 15Z OM VR PK SM HM & ORT 8': '7353 - 15Z OM VAR PK SMKD HM OR TKY 8',
        '7635 - 15Z OM DF RSTTRKY&HNYHM 8': '763500 - 15Z OM DF RSTTRKY&HNYHM 8',
        '8709 - 16Z OM DELI FRESH BLACK FORST HAM 8': '8709 - 16Z OM DELI FRESH BLCK FORST HAM 8',
        '8755 - 14Z OM SELECTS HAM APPLEWOOD SMKD 8': '8755 - 14Z OM SLCTS HAM APPLEWD SMKD 8',
        '9438 - 28Z  OM DELI HAM SALAMI 4': '9438 - 28Z OM DELI HAM SALAMI 4'}
    for key in change_dict:
        df['SKU'].replace(change_dict[key], key, inplace=True)

    return df


def cut_sku(row):
    return row['SKU'][0:4]


def match_missing_sku(row, list_1, df_2):
    if pd.isnull(row['SKU_type']):
        if row['SKU'] in list_1:
            try:
                return df_2[df_2['SKU_short'] == row['SKU_short']][0].values[0]
            except IndexError:
                return row['SKU_type']
    else:
        return row['SKU_type']


def add_sku_type(df):
    data_path_2 = 'data'
    Book1_file_path = 'Book1.xlsx'

    df_b = pd.read_excel(os.path.join(data_path_2, Book1_file_path))
    df_b = df_b.transpose()
    df_b = df_b.reset_index()

    df_b['SKU'] = df_b.apply(lambda row: full_sku(row), axis=1)

    df_b_p = df_b[['SKU', 0]]

    df = adjust_sku(df)

    df = df.merge(df_b_p, how='left', left_on='SKU', right_on='SKU')

    df.rename(columns={0: 'SKU_type'}, inplace=True)

    all_book_unique = list(df_b_p['SKU'].unique())
    all_unique = list(df['SKU'].unique())

    l_2 = []
    for sku in all_unique:
        if sku not in all_book_unique:
            l_2.append(sku)

    df_b_p['SKU_short'] = df_b_p.apply(lambda row: cut_sku(row), axis=1)
    df['SKU_short'] = df.apply(lambda row: cut_sku(row), axis=1)

    df['SKU_type'] = df.apply(
        lambda row: match_missing_sku(row, l_2, df_b_p), axis=1)

    df["SKU_type"].fillna("Unknown", inplace=True)

    return df


@app.route('/api/average_speed_cases_hourly/<start>/<end>/<line>/<quarterly>/<overfill_col>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def average_speed_cases_hourly(start, end, line, quarterly, overfill_col):

    return_object = get_average_speed_cases_hourly(
        start, end, line, quarterly, overfill_col)

    return jsonify(return_object)


@app.route('/api/average_speed_cases_check_weigher/<start>/<end>/<line>/<quarterly>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def average_speed_cases_check_weigher(start, end, line, quarterly):

    return_object = get_average_speed_cases_check_weigher(
        start, end, line, quarterly)

    return jsonify(return_object)


@app.route('/api/target_actual_cases/<start>/<end>/<line>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_target_actual_cases(start, end, line):

    return_object = get_2_values_in_time(
        start_date=start, end_date=end, line=line)

    return jsonify(return_object)


@app.route('/api/sku/<start>/<end>/<line>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_sku(start, end, line):

    return_object = get_value_in_time(
        start_date=start, end_date=end, line=line, col='SKU')

    return jsonify(return_object)


@app.route('/api/cases_produced/<start>/<end>/<line>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_cases_produced(start, end, line):

    return_object = get_value_in_time(
        start_date=start, end_date=end, line=line, col='Cases Produced')

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


@app.route('/api/sku_overfill_heat/<sku>/<quarterly>/<overfill_col>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_sku_overfill_heat(sku: str, quarterly: str, overfill_col):
    quarterly = quarterly == "true"

    return_object = {}
    return_object["Lines"] = {}
    return_object["Date"] = {}
    data = []

    line_counter = 0
    date_counter = 0
    max_overfill = float("-inf")
    min_overfill = float("inf")

    for line in range(1, config.LINE_COUNT):
        if line not in config.LINES_INCOMPLETE:
            if quarterly:
                df = pd.read_csv(
                    f'data/preprocessed_format/quarterhourly_perline/Line_{line}.csv')
            else:
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
                    overfill_v, date) in zip(df[overfill_col], df["Date"])]

                data.extend(data_temp)
                max_for_line = df[overfill_col].quantile(0.98)
                min_for_line = df[overfill_col].quantile(0.02)

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
    return_object["min_colorcode"] = 0 if min_overfill == float(
        "inf") else min_overfill
    return_object["max_colorcode"] = 0 if max_overfill == float(
        "-inf") else max_overfill

    return jsonify(return_object)


@app.route('/api/line_overfill_heat/<line>/<quarterly>/<overfill_col>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_line_overfill_heat(line: str, quarterly: str, overfill_col):
    quarterly = quarterly == "true"

    return_object = {}
    return_object["SKUs"] = {}
    return_object["Date"] = {}
    data = []

    sku_counter = 0
    date_counter = 0

    if line not in config.LINES_INCOMPLETE:
        if quarterly:
            df = pd.read_csv(
                f'data/preprocessed_format/quarterhourly_perline/Line_{line}.csv')
        else:
            df = pd.read_csv(
                f'data/preprocessed_format/hourly_perline/Line_{line}.csv')

        df["Date"] = pd.to_datetime(df["Date"])

    max_overfill = df[overfill_col].quantile(0.98)
    min_overfill = df[overfill_col].quantile(0.02)

    all_skus = list(set(df["SKU"]))
    for sku in all_skus:
        if sku not in return_object["SKUs"]:
            return_object["SKUs"][sku] = sku_counter
            sku_counter += 1

        df_temp_sku = df[df["SKU"] == sku]
        # Adding data in following format [[x-coord-idx1, y-coord-idx1, overfill-value1], [x-coord-idx2, y-coord-idx2, overfill-value2], ...]
        data_temp = [[date, return_object["SKUs"][sku], overfill_v] for (
            overfill_v, date) in zip(df_temp_sku[overfill_col], df_temp_sku["Date"])]

        data.extend(data_temp)

    data = sorted(data)

    for dp in data:
        if dp[0] not in return_object["Date"].keys():
            return_object["Date"][dp[0]] = date_counter
            date_counter += 1
        dp[0] = return_object["Date"][dp[0]]

    return_object["data"] = data
    return_object["Date"] = list(return_object["Date"].keys())
    return_object["SKUs"] = list(return_object["SKUs"].keys())
    return_object["min_colorcode"] = min_overfill
    return_object["max_colorcode"] = max_overfill

    return jsonify(return_object)

# Possible dimensions to include for the PCP


@app.route('/api/get_ai_cw_cols', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_cols():
    return jsonify(list(config.AI_CW_COLS))

# PCP


@app.route('/api/pcp/<line>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_pcp(line, dimensions):
    return_object = {}
    df = pd.read_csv(
        f'data/preprocessed_format/hourly_perline/Line_{line}.csv')
    df = df[dimensions]
    df = df.values.tolist()

    schema = []
    for idx, d in enumerate(dimensions):
        schema.append({"name": d, "index": idx, "text": d})

    return_object["schema"] = schema
    return_object["columns"] = dimensions
    return_object["raw_data"] = df
    return jsonify(return_object)


@app.route('/api/bar_line/<begin_date>/<end_date>/<line>/<quarterly>/<overfill_col>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def bar_line(begin_date, end_date, line, quarterly, overfill_col):
    quarterly = quarterly == "true"
    return_object = {}

    if quarterly:
        df = pd.read_csv(
            f"data/preprocessed_format/quarterhourly_perline/Line_{line}.csv")
    else:
        df = pd.read_csv(
            f"data/preprocessed_format/hourly_perline/Line_{line}.csv")

    df["Date"] = pd.to_datetime(df["Date"])

    df = df[(df["Date"] >= datetime.datetime.strptime(begin_date, "%d-%m-%Y"))
            & (df["Date"] <= datetime.datetime.strptime(end_date, "%d-%m-%Y"))]
    df = add_sku_type(df)
    unique_sku_types = ["Duos", "Base", "Family", "Mega", "PMSU", "Unknown"]
    # unique_sku_types = list(df["SKU_type"].unique())
    overfill_values = {}
    legend = unique_sku_types.copy()
    legend.append("Average Speed")
    overfill_max = max(list(df[overfill_col]))
    overfill_min = min(list(df[overfill_col]))

    for sku in unique_sku_types:
        overfill_values[sku] = []
    for date, overfill_val, sku in zip(df["Date"], df[overfill_col], df["SKU_type"]):

        for sku_u in unique_sku_types:
            if sku == sku_u:
                overfill_values[sku].append(overfill_val)
            else:
                overfill_values[sku].append(0)

    date_values = list(df["Date"])
    hour_strings = []

    for date in date_values:
        hour_strings.append(date)

    avg_speed_values = list(df["Average Speed"])
    speed_max = max(avg_speed_values)
    speed_min = min(avg_speed_values)

    return_object["legend"] = legend
    return_object["hour_strings"] = hour_strings
    return_object["overfill_values"] = overfill_values
    return_object["avg_speed_values"] = avg_speed_values
    return_object["overfill_min"] = overfill_min
    return_object["overfill_max"] = overfill_max
    return_object["speed_min"] = speed_min
    return_object["speed_max"] = speed_max

    return return_object


@app.route('/api/get_available_maps', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_available_maps():
    return jsonify(list(config.OVERFILL_AGGREGATION_OPTIONS))


@app.route('/api/current_overfill_past/<begin_date>/<end_date>/<line>/<overfill_col>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_current_overfill_past(begin_date: str, end_date: str, line: str, overfill_col: str):
    df = pd.read_csv(
        f'data/preprocessed_format/hourly_perline/Line_{line}.csv')
    df["Date"] = pd.to_datetime(df["Date"])

    df = df[(df["Date"] >= datetime.datetime.strptime(begin_date, "%d-%m-%Y"))
            & (df["Date"] <= datetime.datetime.strptime(end_date, "%d-%m-%Y"))]
    overfill = df[overfill_col].sum()

    return jsonify(overfill)


@app.route('/api/current_overfill_present/<line>/<overfill_col>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_current_overfill_present(line: str, overfill_col: str):
    overfill_col = "Overfill"
    return_object = {}
    df = pd.read_csv(
        f'data/preprocessed_format/hourly_perline/Line_{line}.csv')
    df["Date"] = pd.to_datetime(df["Date"])

    current_date = df.tail(1)["Date"]
    current_date_index = current_date.index
    overfill_value = df.tail(1)[overfill_col]

    current_shift = df.tail(1)["Shift"]
    overfill_values = sum(df[(df["Date"].dt.date.reset_index(drop=True) == current_date.dt.date.reset_index(drop=True)[0]) &
                                (df["Shift"].reset_index(drop=True) == current_shift.reset_index(drop=True)[0])][overfill_col])

    return_object["current_date"] = [int(current_date.dt.hour)]
    return_object["overfill_value"] = list(overfill_value)
    return_object["current_shift"] = list(current_shift)
    return_object["overfill_values"] = overfill_values

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
