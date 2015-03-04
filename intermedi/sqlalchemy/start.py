__author__ = 'fabio.lana'

from sqlalchemy import create_engine, Table, MetaData, select
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session

engine = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports', echo=True)
metadata = MetaData(engine)
conn = engine.connect()

conn.execute("SET search_path TO public")

tab_paesi = Table('sparc_wfp_countries', metadata, autoload=True, autoload_with=conn, postgresql_ignore_search_path=True)

s = tab_paesi.select()
rs = s.execute()
paesi_dal_db = rs.fetchall()
paesi = []
for paese in paesi_dal_db:
    paesi.append(paese[0])

users = Table('users', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('name', String(40)),
    Column('age', Integer),
    Column('password', String),
    schema='test'
)
users.create()

emails = Table('emails', metadata,
    Column('email_id', Integer, primary_key=True),
    Column('address', String),
    Column('user_id', Integer, ForeignKey('test.users.user_id')),
    schema='test'
)
emails.create()

i = users.insert()
i.execute(
    {'name': 'Mary', 'age': 30},
    {'name': 'John', 'age': 42},
    {'name': 'Susan', 'age': 57},
    {'name': 'Carl', 'age': 33}
)
i = emails.insert()
i.execute(
    # There's a better way to do this, but we haven't gotten there yet
    {'address': 'mary@example.com', 'user_id': 1},
    {'address': 'john@nowhere.net', 'user_id': 2},
    {'address': 'john@example.org', 'user_id': 2},
    {'address': 'carl@nospam.net', 'user_id': 4},
)

def run(stmt):
    rs = stmt.execute()
    for row in rs:
        print row

# This will return more results than you are probably expecting.
s = select([users, emails])
run(s)

# close it.  if you're using connection pooling, the
# search path is still set up there, so you might want to
# revert it first
conn.close()










