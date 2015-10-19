__author__ = 'fabio.lana'

from sqlalchemy import create_engine, MetaData, select, Table
from sqlalchemy.orm import create_session, session
import pandas as pd
import pycountry
import matplotlib.pylab as plt

engine = create_engine(r'postgresql://geonode:geonode@10.11.40.84/geonode-imports')#, echo=True)
metadata = MetaData(engine, schema='public')
conn = engine.connect()
conn.execute("SET search_path TO public")

session = create_session()
exposed_table = Table('sparc_admin2_cyclones_exposed_population', metadata, autoload=True,  autoload_with=conn, postgresql_ignore_search_path=True)
exposed_country = session.query(exposed_table).filter(exposed_table.c.iso3 == "MDG")
exposed_adm2 = session.query(exposed_table).filter(exposed_table.c.iso3 == "MDG",exposed_table.c.adm2_name == "Andilamena", exposed_table.c.category == 'cat1_5')

# for row in exposed_adm2:
#     print row

affected_table = Table('sparc_admin2_cyclones_affected_pop', metadata, autoload=True,  autoload_with=conn, postgresql_ignore_search_path=True)
affected_country = session.query(affected_table).filter(affected_table.c.iso3 == "MDG")
affected_adm2 = session.query(affected_table).filter(affected_table.c.iso3 == "MDG",affected_table.c.adm2_name == "Andilamena", affected_table.c.category == 'cat1_5')

paese = pycountry.countries.get(name = 'Madagascar')

#exposed_mdg = conn.execute("SELECT * FROM sparc_admin2_cyclones_exposed_population WHERE iso3 = '" + str(paese.alpha3) + "';")
exposed_mdg = conn.execute("SELECT * FROM sparc_admin2_cyclones_exposed_population WHERE iso3 = '" + str(paese.alpha3) + "' AND category = 'cat1_5';")
exposed_df = pd.DataFrame(exposed_mdg.fetchall())
exposed_df.columns = exposed_mdg.keys()
#print exposed_df.describe()

dati_mensili_max = exposed_df.iloc[1:, 10:23]
#print(dati_mensili_max)
#print dati_mensili_max.describe()
massimi_mensili_tutto_paese = (dati_mensili_max[['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']].max(axis=1))

#plt.plot(dati_mensili_max.sep)
plt.title("All adm2 polygons annual people at risk")
#plt.plot(dati_mensili_max.annual)
#plt.plot(massimi_mensili_tutto_paese)
#plt.show()

exposed_mdg_one_adm2 = conn.execute("SELECT * FROM sparc_admin2_cyclones_exposed_population WHERE iso3 = '" + str(paese.alpha3) + "' AND adm2_name = 'Andilamena' AND category = 'cat1_5';")
exposed_df_adm2 = pd.DataFrame(exposed_mdg_one_adm2.fetchall())
exposed_df_adm2.columns = exposed_df_adm2.keys()
dati_mensili_max_adm2 = exposed_df_adm2.iloc[1:, 11:23]
dati_mensili_max_adm2.columns = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
#print dati_mensili_max_adm2
#serie = pd.Series((dati_mensili_max_adm2[['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']].max(axis=0)))
#print serie
#plt.plot(serie)
#plt.show()

#print dati_mensili_max_adm2
dati_mensili_max_adm2_0_30 = exposed_df_adm2.iloc[1:4, 11:23].sum()
dati_mensili_max_adm2_30_70 = exposed_df_adm2.iloc[4:7, 11:23].sum()
dati_mensili_max_adm2_70_100 = exposed_df_adm2.iloc[7:, 11:23].sum()

conn.close()
