__author__ = 'fabio.lana'

from sqlalchemy import create_engine, MetaData, select

engine = create_engine(r'postgresql://geonode:geonode@10.11.40.84/geonode-imports')#, echo=True)
metadata = MetaData(engine, schema='public')
conn = engine.connect()
conn.execute("SET search_path TO public")
conn.close()