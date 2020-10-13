from pathlib import Path
from typing import Union
import datetime as dt
import sqlite3

import pandas as pd
import numpy as np


def metadata(database: Path, table: str = 'dates_contracts') -> pd.DataFrame:

    with sqlite3.connect(database) as db:
        data = pd.read_sql_query(f'SELECT date, contract FROM {table} ORDER BY date,contract;', db)
    return data


def load(database: Path,
         contract: str,
         date: Union[str, dt.date],
         table: str = 'trade_reports') -> pd.DataFrame:

    print(f'loading {contract} -> {date}')

    with sqlite3.connect(database) as db:
        ticks_df = pd.read_sql_query(f'''
SELECT timestamp,price,size FROM {table}
WHERE contract=? AND date=? ORDER BY timestamp;''',
                                     params=(contract, date),
                                     con=db)

    if len(ticks_df) == 0:
        raise ValueError(f'ticks not found for {contract} on date {date}')

    # Drop rows with 0.
    ticks_df = ticks_df[(ticks_df != 0).all(1)]

    # Localize timestamps.
    ts = pd.to_datetime(ticks_df.timestamp, unit='s')
    ts = ts.dt.tz_localize('UTC')
    ts = ts.dt.tz_convert('US/Eastern')
    ticks_df.timestamp = ts

    # Make timestamp row index.
    ticks_df.index = ticks_df.timestamp

    # Drop trades outside market hours.
    ticks_df = ticks_df.between_time('9:30', '16:00')

    # Drop redundent timestamp column.
    ticks_df = ticks_df.drop(axis=1, columns='timestamp')

    # Pice is in cents.
    ticks_df.price = ticks_df.price.apply(lambda x: x * 1e-2)

    # Scale size to shares from lots.
    ticks_df.loc[:, 'size'] *= 1e2

    return ticks_df.reset_index()


def nbars(data: pd.DataFrame, n: int = 20):

    # Group ticks into groups of n.
    groups = data.groupby(data.index // n)

    # Calculate values for each bar.
    cols = ['open', 'high', 'low', 'close', 'volume', 't_open', 't_close']
    data = list()
    for key, item in groups:
        data.append([
            item.iloc[0].price,
            item.price.max(),
            item.price.min(),
            item.iloc[-1].price,
            item.price.sum(),
            item.iloc[0].timestamp,
            item.iloc[-1].timestamp])

    bars_df = pd.DataFrame(data=data, columns=cols)

    # Scale bar open and close timestamps to seconds since market open @ 9.30 am.
    t0 = bars_df.t_open.iloc[0].replace(hour=9, minute=30, second=0).timestamp()
    t1 = bars_df.t_open.iloc[0].replace(hour=16, minute=0, second=0).timestamp()
    td = 1 / (t1 - t0) * (16 - 9.5) * 60 * 60

    bars_df.t_open = bars_df.t_open.apply(lambda x: (x.timestamp() - t0) * td)
    bars_df.t_close = bars_df.t_close.apply(lambda x: (x.timestamp() - t0) * td)

    return bars_df
