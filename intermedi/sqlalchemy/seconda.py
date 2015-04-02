__author__ = 'fabio.lana'

from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import create_session, mapper,session

engine = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports') #, echo=True)
metadata = MetaData(engine,schema='test')
conn = engine.connect()

conn.execute("SET search_path TO test")

users = Table('users', metadata, autoload=True,  autoload_with=conn, postgresql_ignore_search_path=True)
emails = Table('emails', metadata, autoload=True,  autoload_with=conn, postgresql_ignore_search_path=True)

class User(object):
    pass

class Email(object):
    pass

usermapper = mapper(User, users)
emailmapper = mapper(Email, emails)

session = create_session()

mary = session.query(User, users.c.age)
print mary
# close it.  if you're using connection pooling, the
# search path is still set up there, so you might want to
# revert it first
conn.close()










