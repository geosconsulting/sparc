__author__ = 'fabio.lana'
import psycopg2

schema = 'public'
dbname = 'geonode-imports'
host = 'localhost'
user = 'geonode'
password = 'geonode'

try:
    connection_string = "host=%s dbname=%s user=%s password=%s" % (host, dbname, user, password)
    conn = psycopg2.connect(connection_string)
except Exception as e:
    print e.message