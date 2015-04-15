# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

from sqlalchemy import create_engine, MetaData
from geoalchemy2 import Geometry
import pandas as pd

engine = create_engine(r'postgresql://geonode:geonode@127.0.0.1/geonode-imports')
metadata = MetaData(engine,schema='public')
table_area = 'sparc_adm2_area_population'
table_pop = 'sparc_annual_pop'

try:
    conn = engine.connect()
    conn.execute("SET search_path TO public")
except Exception as e:
    print e.message

def collect_data_and_return_df():

    table_pop_returned = pd.read_sql_table(table_pop, engine, index_col='id')
    table_pop_returned['adm2_code'] = table_pop_returned['adm2_code'].astype(int)

    table_area_returned = pd.read_sql_table(table_area, engine, index_col='index')

    return table_area_returned, table_pop_returned

tables = collect_data_and_return_df()
df_area = tables[0][['adm2_code','adm2_name','area_sqkm']]
df_pop =  tables[1][['adm2_code','adm2_name','rp25','rp50','rp100','rp200','rp500','rp1000']]

df_tot = pd.merge(df_area, df_pop, on='adm2_code', how='outer')
area_val = df_tot['area_sqkm']
df_tot['dens_25'] = df_tot['rp25'] / area_val
df_tot['dens_50'] = df_tot['rp50'] / area_val
df_tot['dens_100'] = df_tot['rp100'] / area_val
df_tot['dens_200'] = df_tot['rp200'] / area_val
df_tot['dens_500'] = df_tot['rp500'] / area_val
df_tot['dens_1000'] = df_tot['rp1000'] / area_val

table_name = 'sparc_adm2_population_density'
df_tot.to_sql(table_name, engine, schema='public')







