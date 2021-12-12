from datetime import datetime

LINE_COUNT = 16
LINE_COL = "Line"
DATE_COL = "Date"
SKU_COL = "SKU"
CW_REJECTS_COL = "Weight Result"

CW_id = "CW"
AI_id = "AI"

LINES_INCOMPLETE = {
    2, 9, 10, 12, 15
}
INSTANCE_OFFSET = 100

GRANULAR_REJECT_DATA_PATH = "data/original-format/check-weigher/"
HOURLY_LINESTATS_DATA_PATH = "data/original-format/line-stats/"
QUARTER_HOURLY_LINESTATS_DATA_PATH = "data/original-format/line-stats-quarterly/"

COMBINED_GRANULAR_DATA_PATH = "data/preprocessed_format/assets/check_weigher/"

estimator_params = {
        "input_lag_columns": ["Unit Weight", "Overfill", "Weight Result"],
        "input_lag_cw": 6,
        "relevant_vars_HW": ['Date', 'Rejects', 'OEE', "Shift",
        'Performance', 'Quality', 'Average Speed',
        'DT Events', 'Uptime (min)',
        'Starved (min)', 'Backed Up (min)',
        'LO'],

        "input_temporal_granularities": ["day of week","hour", "year"],#"year"
        #"hot_encode_columns": ["Shift"], #"year"
        #"scaling": "min_max",

        # Following two variables must sum up to 10
        "train_mass": 9,
        "test_mass": 1,
        "label_window": 3,
        "label": "Weight Result", # Could also be Weight_Result
        "label_mold": "cummulative", # Could also be point
}

MODELS_PATH = "serialized_forecasting_models/keras/"

MODEL_NAMES = {
    "Line 3": "WR3.pickle.dat",
    "Line 1": "WR1.pickle.dat"
}

N_TENDENCY = 100
#datetime(year, month, day, hour, minute, second, microsecond)
CURRENT_MODEL_TYPE = "lstm"
CURRENT_DATE = datetime(2021, 9, 27, 12, 0, 0)