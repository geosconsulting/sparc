__author__ = 'fabio.lana'

from sqlalchemy import create_engine, Table, MetaData,select
from sqlalchemy.orm import create_session, mapper, session
from geoalchemy2 import Geometry

engine = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports',echo=True)
metadata = MetaData(engine)
conn = engine.connect()

tab_amin_all = Table('sparc_gaul_wfp_iso', metadata, autoload=True, autoload_with=conn, postgresql_ignore_search_path=True)
s = tab_amin_all.select()
rs = s.execute()
admin_dal_db = rs.fetchall()

select(tab_amin_all.c.adm0_name == 'Benin')

conn.close()










