__author__ = 'fabio.lana'

from sqlalchemy import create_engine, MetaData
import pandas as pd

engine = create_engine(r'postgresql://geonode:geonode@127.0.0.1/geonode-imports')
metadata = MetaData(engine,schema='public')
tbl_rp_name = 'sparc_adm2_population_rp'
tbl_pop_name = 'sparc_adm2_area_population'

try:
    conn = engine.connect()
    conn.execute("SET search_path TO public")
except Exception as e:
    print e.message

df_rp = pd.read_sql_table(tbl_rp_name, engine, index_col='index')
df_pop = pd.read_sql_table(tbl_pop_name, engine, index_col='index')
df_tot = pd.merge(df_pop, df_rp, on='adm2_code', how='outer')

area_val = df_tot['area_sqkm_x']
pop_val = df_tot['pop']
df_tot['density'] = pop_val / area_val
df_tot['perc_25'] = df_tot['rp25'] / pop_val * 100
df_tot['perc_50'] = df_tot['rp50'] / pop_val * 100
df_tot['perc_100'] = df_tot['rp100'] / pop_val * 100
df_tot['perc_200'] = df_tot['rp200'] / pop_val * 100
df_tot['perc_500'] = df_tot['rp500'] / pop_val * 100
df_tot['perc_1000'] = df_tot['rp1000'] / pop_val * 100
df_tot['dens_25'] = df_tot['rp25'] / area_val
df_tot['dens_50'] = df_tot['rp50'] / area_val
df_tot['dens_100'] = df_tot['rp100'] / area_val
df_tot['dens_200'] = df_tot['rp200'] / area_val
df_tot['dens_500'] = df_tot['rp500'] / area_val
df_tot['dens_1000'] = df_tot['rp1000'] / area_val

print df_tot.head()

#table_adm2_density = 'sparc_adm2_density'
#df_tot.to_sql(table_adm2_density, engine, schema='public')