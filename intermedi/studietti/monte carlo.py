__author__ = 'fabio.lana'

#http://adventuresinoptimization.blogspot.it/2009/10/easy-monte-carlo-simulation-in-python.html

import random
import pandas as pd
from sqlalchemy import create_engine, MetaData

PASSENGERS = 100.0
TRAINS     =   5.0
ITERATIONS = 10000

def sim():
    passengers = 0.0

    # Determine when the train arrives
    train = random.expovariate(TRAINS)

    # Count the number of passenger arrivals before the train
    now = 0.0
    while True:
        now += random.expovariate(PASSENGERS)
        if now >= train:
            break
        passengers += 1.0

    return passengers

def rain_table():

    engine_in = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports')
    try:
        conn_in = engine_in.connect()
        metadata_in = MetaData(engine_in)
        conn = engine_in.connect()
        conn.execute("SET search_path TO public")
    except Exception as e:
        print e.message

    precipitation = pd.read_sql_table('sparc_month_prec_norm', engine_in, index_col='adm2_code')

    return precipitation

if __name__ == '__main__':
    # output = [sim() for _ in xrange(ITERATIONS)]
    #
    # total = sum(output)
    # mean = total / len(output)
    #
    # sum_sqrs = sum(x*x for x in output)
    # variance = (sum_sqrs - total * mean) / (len(output) - 1)
    #
    # print 'E[X] = %.02f' % mean
    # print 'Var(X) = %.02f' % variance
    rito_ambrosiano =  rain_table()
    print rito_ambrosiano[['adm2_name','jan']][33087]
