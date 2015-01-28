__author__ = 'fabio.lana'

import psycopg2
from psycopg2.extras import RealDictCursor

class DB(object):

    def db_connect(self):
        schema = 'public'
        dbname = 'geonode-imports'
        user = 'geonode'
        password = 'geonode'
        connection_string = "dbname=%s user=%s password=%s" % (dbname, user, password)
        db_connessione = psycopg2.connect(connection_string)
        db_connessione.cursor_factory = RealDictCursor
        db_cursore = db_connessione.cursor()
        return db_cursore


    def valuti_paesi(self,db_cursore):
        sql = "SELECT DISTINCT name FROM sparc_wfp_countries;"
        db_cursore.execute(sql);
        risultati = db_cursore.fetchall()

        paesi = []
        for paese in risultati:
            paesi.append(paese['name'].strip())

        return paesi

    def valori_amministrativi(self,db_cursore,paese_ricerca):
        sql = "SELECT name,iso2,iso3 FROM sparc_wfp_countries WHERE name = '" + paese_ricerca + "';"
        db_cursore.execute(sql);
        risultati = db_cursore.fetchall()
        return risultati


objDB = DB()
connessione = objDB.db_connect()
print objDB.valuti_paesi(connessione)
print objDB.valori_amministrativi(connessione,"Sudan")[0]['iso3']






