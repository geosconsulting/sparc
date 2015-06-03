__author__ = 'fabio.lana'

import pandas as pd
from sqlalchemy import create_engine, MetaData

def sqlAlch_connect(ip_in, table_flood, table_rain):

    engine = create_engine(r'postgresql://geonode:geonode@'+ ip_in + '/geonode-imports')
    try:
        conn_in = engine.connect()
        metadata_in = MetaData(engine)
        conn = engine.connect()
        conn.execute("SET search_path TO public")
    except Exception as e:
        print e.message

    df_flood = pd.read_sql_table(table_flood, engine, index_col='disaster_no')
    df_rain = pd.read_sql_table(table_rain, engine, index_col='id')

    return df_flood, df_rain


def main():

    ip_in = '127.0.0.1'
    table_floods = 'sparc_emdat_scraping_Flood'
    table_rain = 'sparc_month_prec'
    il_paese = 'Benin'

    tabelle = sqlAlch_connect(ip_in, table_floods, table_rain)

    tab_paese = tabelle[0][tabelle[0]['country_name'] == il_paese]
    print tab_paese.groupby(['end_date']).head()


if __name__ == "__main__":
    main()
