__author__ = 'fabio.lana'

#pg_dump -f drought_first.sql --table sparc_population_month_drought -U geonode geonode-imports

import psycopg2

host = '10.65.57.131'
port = '5432'
schema = 'public'
dbname = 'test'
user = 'geonode'
password = 'geonode'

connection_string = "host=%s port=%s dbname=%s user=%s password=%s" % (host, port, dbname, user, password)

try:
    conn = psycopg2.connect(connection_string)
    print "Connection opened"
except Exception as e:
    print e.message

# cur = conn.cursor()
#
# try:
#     cur.close()
#     conn.close()
#     print "Connection closed"
# except:
#     print "Problem in closing the connection"