__author__ = 'fabio.lana'

import pandas as pd
from sqlalchemy import create_engine, MetaData
import sys


def sqlalch_connect(ip_in, ip_out, table_name):

    engine_in = create_engine(r'postgresql://geonode:geonode@' + ip_in + '/geonode-imports')
    try:
        conn_in = engine_in.connect()
        metadata_in = MetaData(engine_in)
        conn = engine_in.connect()
        conn.execute("SET search_path TO public")
    except Exception as e:
        print e.message

    df_in_sql = pd.read_sql_table(table_name, engine_in, index_col='id')

    engine_out = create_engine(r'postgresql://geonode:geonode@' + ip_out + '/geonode-imports')
    try:
        conn_out = engine_out.connect()
    except Exception as e:
        print e.message

    df_in_sql.to_sql(table_name, engine_out, schema='public')

def main():
    ip_in = '127.0.0.1'
    ip_out = '10.65.57.63'
    tables = ['sparc_population_month']
    for table_name in tables:
        sqlalch_connect(ip_in, ip_out, table_name)

if __name__ == "__main__":
    main()