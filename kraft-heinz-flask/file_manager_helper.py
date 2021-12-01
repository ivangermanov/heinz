import pandas as pd
import os
import config


def get_hourly(line: str, dir_linestats: str) -> pd.DataFrame():
    files = os.listdir(dir_linestats)
    df_toconcat = []

    for fn in files:
        df_line = pd.read_csv(os.path.join(
            dir_linestats, fn))
        df_line = df_line[df_line[config.LINE_COL] == line]
        df_toconcat.append(df_line)

    return pd.concat(df_toconcat)
