__author__ = 'fabio.lana'

from sqlalchemy import create_engine, MetaData, select, Table
from sqlalchemy.orm import create_session, session
import pandas as pd

engine = create_engine(r'postgresql://geonode:geonode@10.11.40.84/geonode-imports')#, echo=True)
metadata = MetaData(engine, schema='public')
conn = engine.connect()
conn.execute("SET search_path TO public")

session = create_session()
exposed_table = Table('sparc_admin2_cyclones_exposed_population', metadata, autoload=True,  autoload_with=conn, postgresql_ignore_search_path=True)
exposed_country = session.query(exposed_table).filter(exposed_table.c.iso3 == "MDG")
exposed_adm2 = session.query(exposed_table).filter(exposed_table.c.iso3 == "MDG",exposed_table.c.adm2_name == "Andilamena",exposed_table.c.category == 'cat1_5')

# for row in exposed_adm2:
#     print row

affected_table = Table('sparc_admin2_cyclones_affected_pop', metadata, autoload=True,  autoload_with=conn, postgresql_ignore_search_path=True)
affected_country = session.query(affected_table).filter(affected_table.c.iso3 == "MDG")
affected_adm2 = session.query(affected_table).filter(affected_table.c.iso3 == "MDG",affected_table.c.adm2_name == "Andilamena",affected_table.c.category == 'cat1_5')

affected_mdg = conn.execute("SELECT * FROM sparc_admin2_cyclones_affected_pop WHERE iso3 = 'MDG';")
affected_df = pd.DataFrame(affected_mdg.fetchall())
affected_df.columns = affected_mdg.keys()
print affected_df

conn.close()
