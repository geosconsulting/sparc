__author__ = 'fabio.lana'

import psycopg2
import pandas as pd
from sqlalchemy import create_engine

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

    def create_sparc_gdelt_table_historic(self, table):

        SQL = "CREATE TABLE %s.%s %s %s"
        campi = """(
            id serial NOT NULL,
            globaleventid integer,
            sqldate integer,
            monthyear character(6),
            year character(4),
            fractiondate double precision,
            actor1code character(6),
            actor1name character(255),
            actor1countrycode character(6),
            actor1knowngroupcode character(6),
            actor1ethniccode character(6),
            actor1religion1code character(6),
            actor1religion2code character(6),
            actor1type1code character(6),
            actor1type2code character(6),
            actor1type3code character(6),
            actor2code character(6),
            actor2name character(255),
            actor2countrycode character(6),
            actor2knowngroupcode character(6),
            actor2ethniccode character(6),
            actor2religion1code character(6),
            actor2religion2code character(6),
            actor2type1code character(6),
            actor2type2code character(6),
            actor2type3code character(6),
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
            actor2geo_featureid integer,
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

    def inserisci_valori_storici_gdelt(self, linea):

        #for linea in listone:
            print linea
            inserimento = "INSERT INTO " + self.schema + ".sparc_gdelt_archive" + \
                          " (globaleventid, sqldate,monthyear,year,fractiondate,actor1code,actor1name," \
                          "actor1countrycode,actor1knowngroupcode,actor1ethniccode,actor1religion1code," \
                          "actor1religion2code,actor1type1code,actor1type2code,actor1type3code,actor2code," \
                          "actor2name,actor2countrycode,actor2knowngroupcode,actor2ethniccode,actor2religion1code,"\
                          "actor2religion2code,actor2type1code,actor2type2code,actor2type3code,isrootevent,"\
                          "eventcode,eventbasecode,eventrootcode,quadclass,goldsteinscale,nummentions,numsources,"\
                          "numarticles,avgtone," \
                          "actor1geo_type,actor1geo_fullname,actor1geo_countrycode,actor1geo_adm1code,actor1geo_lat,actor1geo_long,actor1geo_featureid,"\
                          "actor2geo_type,actor2geo_fullname,actor2geo_countrycode,actor2geo_adm1code,actor2geo_lat,actor2geo_long,actor2geo_featureid,"\
                          "actiongeo_type,actiongeo_fullname,actiongeo_countrycode,actiongeo_adm1code,actiongeo_lat,actiongeo_long,actiongeo_featureid,"\
                          "dateadded)" \
                          "VALUES('" + linea[0] + "','" + linea[1] + "'," + linea[2] + "," + linea[3] + "," + linea[4] + ",'" + linea[5] + "','" + linea[6] + "','" + linea[7] + "','" \
                                     + linea[8] + "','" + linea[9] + "','" + linea[10] + "','" + linea[11] + "','" + linea[12] + "','" + linea[13] + "','" + linea[14] + "','" + linea[15] + "','" \
                                     + linea[16] + "','" + linea[17] + "','" + linea[18] + "','" + linea[19] + "','" + linea[20] + "','" + linea[21] + "','" + linea[22] + "','" + linea[23] + "','" \
                                     + linea[24] + "'," + linea[25] + "," + linea[26] + "," + linea[27] + "," + linea[28] + "," + linea[29] + "," + linea[30] + "," + linea[31] + "," \
                                     + linea[32] + "," + linea[33] + "," + linea[34] + ",'" + linea[35] + "','" + linea[36] + "','" + linea[37] + "','" + linea[38] + "'," + linea[39] + "," \
                                     + linea[40] + "," + linea[41] + ",'" + linea[42] + "','" + linea[43] + "','" + linea[44] + "','" + linea[45] + "'," + linea[46] + "," + linea[47] + "," \
                                     + linea[48] + ",'" + linea[49] + "','" + linea[50] + "','" + linea[51] + "','" + linea[52] + "'," + linea[53] + "," + linea[54] + ",'" + linea[55] + "'," \
                                     + str(int(linea[56])).replace('\n','') + ");"
            print inserimento
            self.db_cursore.execute(inserimento)

    def salva_cambi(self):

        try:
            self.db_connessione.commit()
            print "Changes saved"
        except psycopg2.Error as createErrore:
            print createErrore.pgerror

    def depickle_pandas_historical(self,paese):

        local_path = 'C:/data/tools/sparc/conflicts/SPARC_GDELT/test_data/results/'
        filolo = local_path + paese + '.pickle'
        file_pickle = pd.io.pickle.read_pickle(filolo)
        lunghezza =len(file_pickle)

        d = {}
        for numerico in range(0,lunghezza):
            lina = file_pickle[0][numerico]
            lina_split = lina.split("\t")
            #print lina_split
            altri = lina_split[1:]
            aggiunta = [x for x in altri]
            d[lina_split[0]] = aggiunta
        df = pd.DataFrame(data=d)


        #print type(df)
        d_trans = df.transpose()
        d_trans.columns = ['iso','actor1','type','id1','id2','id3','id4','id5','id6','id7','id8','id9','id10','id11','id12','id13']

        print d_trans.head()

        engine = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports')

        connection = engine.connect()
        d_trans.to_sql('gd_' + str(paese), engine, schema='conflicts', chunksize=1000)
        connection.close()

        return d_trans
