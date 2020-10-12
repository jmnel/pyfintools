import sqlite3
from pprint import pprint

import pandas as pd

with sqlite3.connect('ib.sqlite3') as db:
    df = pd.read_sql_query(
        'SELECT timestamp, price, size FROM ib_trade_reports WHERE symbol="KODK" and day="2020-07-30" ORDER BY timestamp;',
        db)

df = df[(df != 0).all(1)]

# print(df['timestamp'].head())
ts = pd.to_datetime(df.timestamp, unit='s')
ts = ts.dt.tz_localize('UTC')
ts = ts.dt.tz_convert('US/Eastern')
df.timestamp = ts

df.index = df.timestamp
df = df.between_time('9:30', '16:00')
df.index = df['timestamp'].dt.time

df = df.drop(axis=1, columns='timestamp')

df.price = df.price.apply(lambda x: x * 1e-2)
df.loc[:, 'size'] *= 1e2
#df.size = df.size * 1e2

print(df.head())
