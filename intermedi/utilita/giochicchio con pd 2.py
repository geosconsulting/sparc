__author__ = 'fabio.lana'

import pandas.io.sql as psql
import psycopg2 as pg
import pandas as pd
import numpy as np

schema = 'public'
dbname = 'sparc_old'
user = 'postgres'
password = 'antarone'
connection_string = "dbname=%s user=%s password=%s" % (dbname, user, password)
connection = pg.connect(connection_string)

dataframe = psql.read_sql("SELECT * FROM actor", connection)
