__author__ = 'fabio.lana'

import pandas as pd
from sqlalchemy import create_engine, MetaData


def sqlalch_connect(ip_in, ip_out, table_name):

    engine_in = create_engine(r'postgresql://geonode:geonode@' + ip_in + '/geonode-imports')
    try:
        conn_in = engine_in.connect()
        metadata_in = MetaData(engine_in)
        conn = engine_in.connect()
        conn.execute("SET search_path TO public")
    except Exception as e:
        print e.message

    # SUPERATO DALLA LETTURA DIRETTA DA SQL CON PANDAS SQLALCHEMY
    # tab_pop_annual = Table(table_name, metadata_in, autoload=True, autoload_with=conn,
    #                       postgresql_ignore_search_path=True)
    # s = tab_pop_annual.select()
    # rs = s.execute()
    # annual_pop_flood = rs.fetchall()
    # df_in_sql = pd.DataFrame(annual_pop_flood)
    # df_in_sql.columns = ['id','iso3','adm0_name','adm0_code','adm1_code','adm1_name','adm2_code',
    # 'adm2_name','rp25','rp50','rp100','rp200','rp500','rp1000']
    # SUPERATO DALLA LETTURA DIRETTA DA SQL CON PANDAS SQLALCHEMY

    df_in_sql = pd.read_sql_table(table_name, engine_in, index_col='id')
    engine_out = create_engine(r'postgresql://geonode:geonode@' + ip_out + '/geonode-imports')
    try:
        conn_out = engine_out.connect()
    except Exception as e:
        print e.message

    df_in_sql.to_sql(table_name, engine_out, schema='public')


def main():
    ip_in = '127.0.0.1'
    ip_out = '10.65.57.81'
    tables = ['sparc_annual_pop', 'sparc_population_month', 'sparc_population_month_drought']
    for table_name in tables:
        sqlalch_connect(ip_in, ip_out, table_name)


if __name__ == "__main__":
    main()