import sqlite3

import numpy as np

db = sqlite3.connect('ib.sqlite3')

db.execute('DROP TABLE IF EXISTS dates_contracts;')
db.execute('''
CREATE TABLE dates_contracts(
    id INTEGER PRIMARY KEY,
    date DATETIME NOT NULL,
    contract CHAR(16) NOT NULL,
    tick_count INTEGER NOT NULL DEFAULT(0));''')

db.close()
