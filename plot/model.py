from pathlib import Path
import datetime as dt

import pandas as pd
import numpy as np

import sqlite3


class TickModel:

    def __init__(self, database: Path):
        self.db_path = database

        self.__load_meta()

    def __load_meta(self):

        with sqlite3.connect(self.db_path) as db:
            self._meta = pd.read_sql_query('SELECT date, contract FROM dates_contracts ORDER BY date;', db)

    @property
    def meta(self):
        return self._meta

    def contracts(self):
        return np.sort(self._meta.contract.unique())

    def dates(self):
        return np.sort(self._meta.date.unique())

    def load_ticks(self, contract, date):

        match = self._meta[(self._meta.contract == contract) & (self._meta.date == date)]

        if len(match) != 1:
            raise ValueError(f'ticks not found for {contract} on {date}')

        with sqlite3.connect('ib.sqlite3') as db:
            ticks_df = pd.read_sql_query('''
SELECT timestamp, price, size FROM trade_reports WHERE contract=? and date=? ORDER BY timestamp;''',
                                         params=(contract, date),
                                         con=db)
            assert len(ticks_df) > 0

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

        self.ticks_df = ticks_df.reset_index()

        self.contract = contract
        self.date = date

    def tick_bars(self, n: int = 20):

        # Group ticks into groups of n.
        r = self.ticks_df.groupby(self.ticks_df.index // n)

        # Calculate values for each bar.
        cols = ['open', 'high', 'low', 'close', 'volume', 't_open', 't_close']
        data = list()
        for key, item in r:
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

        self.bars_df = bars_df


#model = TickModel('ib.sqlite3')
#model.load_ticks('KODK', '2020-07-29')
# model.tick_bars(20)
