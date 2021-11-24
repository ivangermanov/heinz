import pandas as pd
import numpy as np
import os
import src.constants

def get_hourly(line: str, dir_linestats: str) -> pd.DataFrame():
    files = os.listdir(dir_linestats)
    df_toconcat = []

    for fn in files:
        df_line = pd.read_excel(os.path.join(dir_linestats, fn))
        df_line = df_line[df_line[src.constants.LINE_COL]==line]
        df_toconcat.append(df_line)

    return pd.concat(df_toconcat)