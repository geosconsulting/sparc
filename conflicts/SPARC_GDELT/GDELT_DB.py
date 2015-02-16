__author__ = 'fabio.lana'

import psycopg2
from psycopg2.extras import RealDictCursor

class GDELT_DB(object):

    def __init__(self, host, schema, dbname, user, password):

        self.host = host
        self.schema = schema
        self.dbname = dbname
        self.user = user
        self.password = password
        self.db_connessione = None
        self.db_cursore = None

    def apri_connessione(self):

        connection_string = "dbname=%s user=%s password=%s host=%s" % (self.dbname, self.user, self.password, self.host)
        try:
            self.db_connessione = psycopg2.connect(connection_string)
            self.db_cursore = self.db_connessione.cursor()
            print("Connessione attiva")
        except:
            print("No connection")

    def chiudi_connessione(self):

        try:
            self.db_cursore.close()
            self.db_connessione.close()
            print("Connessione chiusa")
        except:
            print "Problem in closing the connection"

    def gather_paesi(self):

        sql = "SELECT DISTINCT name FROM sparc_wfp_countries;"
        self.db_cursore.execute(sql);
        risultati = self.db_cursore.fetchall()

        paesi = []
        for paese in risultati:
            paesi.append(paese[0].strip())

        return paesi

    def country_codes(self, paese_ricerca):

        sql = "SELECT name,iso2,iso3,fips FROM sparc_wfp_countries WHERE name = '" + paese_ricerca + "';"

        self.db_cursore.execute(sql)
        risultati = self.db_cursore.fetchall()

        return risultati

    def boundinbox_paese(self, paese_ricerca):

        sql = "SELECT ST_Extent(geom) as extent FROM sparc_gaul_wfp_iso WHERE adm0_name = '" + paese_ricerca + "';"
        self.db_cursore.execute(sql);
        bbox = self.db_cursore.fetchall()

        llat = float(bbox[0][0].split("(")[1].split(" ")[0])
        llon = float(bbox[0][0].split("(")[1].split(" ")[1].split(",")[0])
        #print llat, llon

        ulat = float(bbox[0][0].split(",")[1].split(" ")[0])
        ulon = float(bbox[0][0].split(",")[1].split(" ")[1].replace(")",""))
        #print ulat, ulon

        lat_paese = float(ulat) - float(llat)
        lon_paese = float(ulon) - float(llon)
        centro_lat = lat_paese/2
        centro_lon = lon_paese/2

        return centro_lat, centro_lon, llat,llon, ulat, ulon

    def check_tabella(self, table_name):

            esiste_tabella = "SELECT '" + self.schema + "." + table_name + "'::regclass"
            try:
                self.db_cursore.execute(esiste_tabella)
                return "exists"
            except psycopg2.ProgrammingError as laTabellaNonEsiste:
                descrizione_errore = laTabellaNonEsiste.pgerror
                codice_errore = laTabellaNonEsiste.pgcode
                return descrizione_errore, codice_errore

    def create_sparc_gdelt_table(self, table):

        SQL = "CREATE TABLE %s.%s %s %s"
        campi = """(
            id serial NOT NULL,
            globaleventid integer,
            sqldate integer,
            monthyear character(6),
            year character(4),
            fractiondate double precision,
            actor1code character(3),
            actor1name character(255),
            actor1countrycode character(3),
            actor1knowngroupcode character(3),
            actor1ethniccode character(3),
            actor1religion1code character(3),
            actor1religion2code character(3),
            actor1type1code character(3),
            actor1type2code character(3),
            actor1type3code character(3),
            actor2code character(3),
            actor2name character(255),
            actor2countrycode character(3),
            actor2knowngroupcode character(3),
            actor2ethniccode character(3),
            actor2religion1code character(3),
            actor2religion2code character(3),
            actor2type1code character(3),
            actor2type2code character(3),
            actor2type3code character(3),
            isrootevent integer,
            eventcode character(4),
            eventbasecode character(4),
            eventrootcode character(4),
            quadclass integer,
            goldsteinscale double precision,
            nummentions integer,
            numsources integer,
            numarticles integer,
            avgtone double precision,
            actor1geo_type integer,
            actor1geo_fullname character(255),
            actor1geo_countrycode character(2),
            actor1geo_adm1code character(4),
            actor1geo_lat double precision,
            actor1geo_long double precision,
            actor1geo_featureid integer,
            actor2geo_type integer,
            actor2geo_fullname character(255),
            actor2geo_countrycode character(2),
            actor2geo_adm1code character(4),
            actor2geo_lat double precision,
            actor2geo_long double precision,
            ctor2geo_featureid integer,
            actiongeo_type integer,
            actiongeo_fullname character(255),
            actiongeo_countrycode character(2),
            actiongeo_adm1code character(4),
            actiongeo_lat double precision,
            actiongeo_long double precision,
            actiongeo_featureid integer,
            dateadded integer,"""
        constraint = "CONSTRAINT sparc_gdelt_archive_pkey PRIMARY KEY (id));"

        comando = SQL % (self.schema, table, campi, constraint)
        #print comando

        try:
            self.db_cursore.execute(comando)
            print "GDELT Table Created"
        except psycopg2.Error as createErrore:
            descrizione_errore = createErrore.pgerror
            codice_errore = createErrore.pgcode
            return descrizione_errore, codice_errore

    def inserisci_valori_calcolati(self):

        pass
        # for linea in lista_finale:
        #     inserimento = "INSERT INTO " + self.schema + ".sparc_population_month" + \
        #                   " (iso3, adm0_name,adm0_code,adm1_name,adm1_code,adm2_code,adm2_name," \
        #                   "rp,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,\"dec\", n_cases)" \
        #                   "VALUES('" + str(linea[0]) + "','" + linea[1] + "'," + linea[2] + ",'" + linea[3] + "'," \
        #                              + linea[4] + "," + linea[5] + ",'" + linea[6] + "'," + linea[7] + "," \
        #                              + linea[8] + "," + linea[9] + "," + linea[10] + "," + linea[11] + "," \
        #                              + linea[12] + "," + linea[13] + "," + linea[14] + "," + linea[15] + "," \
        #                              + linea[16] + "," + linea[17] + "," + linea[18] + "," + linea[19] + "," \
        #                              + linea[20] + ");"
        #     #print inserimento
        #     self.cur.execute(inserimento)

    def salva_cambi(self):

        try:
            self.db_connessione.commit()
            print "Changes saved"
        except psycopg2.Error as createErrore:
            print createErrore.pgerror

host = 'localhost'
schema = 'public'
dbname = 'geonode-imports'
user = 'geonode'
password = 'geonode'
table = 'sparc_gdelt_archive'

objDB = GDELT_DB(host, schema, dbname, user, password)

objDB.apri_connessione()
paesi = objDB.gather_paesi()
objDB.chiudi_connessione()

objDB.apri_connessione()
admin = objDB.country_codes('Sudan')[0]
objDB.chiudi_connessione()

objDB.apri_connessione()
bbox = objDB.boundinbox_paese('Sudan')
objDB.chiudi_connessione()

objDB.apri_connessione()
controllo = objDB.check_tabella('sparc_gdelt_archive')
objDB.chiudi_connessione()

if controllo[1] == '42P01':
     objDB.apri_connessione()
     objDB.create_sparc_gdelt_table(table)
     objDB.salva_cambi()
     objDB.chiudi_connessione()
else :
    pass
