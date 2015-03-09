__author__ = 'fabio.lana'

import os
import dbf
import fileinput
import psycopg2
import glob

schema = 'public'
dbname = 'geonode-imports'
user = 'geonode'
password = 'geonode'
connection_string = "dbname=%s user=%s password=%s" % (dbname, user, password)
direttorio_radice = "C:/data/tools/sparc/projects/"

def read_monthly_values_country_fromTXT(paese_ricerca):

    file = direttorio_radice + paese_ricerca + "/" + paese_ricerca + ".txt"
    list_monthly_values = []
    for line in fileinput.input(file):
        list_monthly_values.append(line.strip("\n"))
    return list_monthly_values

def create_sparc_population_annual_table():

    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()

    SQL = "CREATE TABLE %s.%s %s %s;"
    campi = """(
          id serial NOT NULL,
          iso3 character(3),
          adm0_name character(120),
          adm0_code character(12),
          adm1_code character(12),
          adm1_name character(120),
          adm2_code character(12),
          adm2_name character(120),
          rp25 integer,
          rp50 integer,
          rp100 integer,
          rp200 integer,
          rp500 integer,
          rp1000 integer,"""
    constraint = "CONSTRAINT pk_annual_pop PRIMARY KEY (id));"

    try:
        comando = SQL % (schema, 'sparc_annual_pop', campi, constraint)
        cur.execute(comando)
        print "Annual Population Table Created"
    except psycopg2.Error as createErrore:
        descrizione_errore = createErrore.pgerror
        codice_errore = createErrore.pgcode
        print descrizione_errore, codice_errore

    conn.commit()
    cur.close()
    conn.close()

def create_sparc_population_monthly_table():

    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()

    SQL = "CREATE TABLE %s.%s %s %s;"
    campi = """(
        id serial,
        iso3 character(3),
        adm0_name character(120),
        adm0_code character(8),
        adm1_name character(120),
        adm1_code character(8),
        adm2_code character(8),
        adm2_name character(120),
        rp integer,
        jan integer,
        feb integer,
        mar integer,
        apr integer,
        may integer,
        jun integer,
        jul integer,
        aug integer,
        sep integer,
        oct integer,
        nov integer,
        dec integer,
        n_cases double precision,"""
    constraint = "CONSTRAINT population_month_pkey PRIMARY KEY (id));"

    try:
        comando = SQL % (schema, 'sparc_population_month', campi, constraint)
        cur.execute(comando)
        print "Monthly Population Table Created"
    except psycopg2.Error as createErrore:
        descrizione_errore = createErrore.pgerror
        codice_errore = createErrore.pgcode
        print descrizione_errore, codice_errore

    conn.commit()
    cur.close()
    conn.close()

def collect_annual_data_byRP_from_dbf_country(paese_ricerca):

    contatore_si = 0
    lista_si_dbf = []

    direttorio = direttorio_radice + paese_ricerca
    dct_valori_inondazione_annuale = {}
    for direttorio_principale, direttorio_secondario, file_vuoto in os.walk(direttorio):
        if direttorio_principale != direttorio:
            paese = direttorio_principale.split("/")[5].split("\\")[0]
            admin = direttorio_principale.split(paese)[1][1:]
            files_dbf = glob.glob(direttorio_principale + "/*.dbf")
            for file in files_dbf:
                fileName, fileExtension = os.path.splitext(file)
                if 'stat' in fileName:
                    contatore_si += 1
                    lista_si_dbf.append(direttorio_principale)
                    try:
                        filecompleto = fileName + ".dbf"
                        tabella = dbf.Table(filecompleto)
                        tabella.open()
                        dct_valori_inondazione_annuale[admin] = {}
                        for recordio in tabella:
                            if recordio.value > 0:
                                dct_valori_inondazione_annuale[admin][recordio.value] = recordio.sum
                    except:
                        pass

    lista_stat_dbf = [25, 50, 100, 200, 500, 1000]
    for valore in dct_valori_inondazione_annuale.items():
        quanti_rp = len(valore[1].keys())
        if quanti_rp < 6:
            for rp in lista_stat_dbf:
                if rp not in valore[1].keys():
                    dct_valori_inondazione_annuale[valore[0]][rp] = 0

    return contatore_si,lista_si_dbf, dct_valori_inondazione_annuale

def process_dct_annuali(adms, dct_valori_inondazione_annuale):

    db_connessione = psycopg2.connect(connection_string)
    db_cursore = db_connessione.cursor()

    lista = []
    for adm in adms:
        #print adm
        sql = "SELECT DISTINCT iso3, adm0_name, adm0_code, adm1_code,adm1_name, adm2_name, adm2_code FROM sparc_population_month WHERE adm2_code = '" + adm + "' AND adm0_name = '" + paese_ricerca + "';"
        #print sql
        db_cursore.execute(sql)
        risultati = db_cursore.fetchall()
        lista.append(risultati)

    dct_valori_amministrativi = {}
    for indice in range(0, len(lista)):
        radice_dct = lista[indice][0][6].strip()
        dct_valori_amministrativi[radice_dct] = {}
        dct_valori_amministrativi[radice_dct]["iso3"] = str(lista[indice][0][0].strip())
        dct_valori_amministrativi[radice_dct]["adm0_name"] = str(lista[indice][0][1].strip())
        dct_valori_amministrativi[radice_dct]["adm0_code"] = str(lista[indice][0][2].strip())
        dct_valori_amministrativi[radice_dct]["adm1_code"] = str(lista[indice][0][3].strip())
        dct_valori_amministrativi[radice_dct]["adm1_name"] = str(lista[indice][0][4].strip())
        dct_valori_amministrativi[radice_dct]["adm2_name"] = str(lista[indice][0][5].strip())
        dct_valori_amministrativi[radice_dct]["adm2_code"] = str(lista[indice][0][6].strip())
    #print dct_valori_amministrativi


    lista_rp = [25, 50, 100, 200, 500, 1000]
    for valore in dct_valori_inondazione_annuale.items():
        quanti_rp = len(valore[1].keys())
        if quanti_rp < 6:
            for rp in lista_rp:
                if rp not in valore[1].keys():
                    dct_valori_inondazione_annuale[valore[0]][rp] = 0

    linee =[]
    for amministrativa_dct_amministrativi in dct_valori_amministrativi.items():
        adm2_amministrativa = amministrativa_dct_amministrativi[0]
        for amministrativa_dct_inondazione in dct_valori_inondazione_annuale.items():
            if amministrativa_dct_inondazione[0].split("_")[1] == adm2_amministrativa:
                linee.append(str(amministrativa_dct_amministrativi[1]['iso3']).upper() + "','" + str(amministrativa_dct_amministrativi[1]['adm0_name']).capitalize() + "'," + amministrativa_dct_amministrativi[1]['adm0_code'] +
                             ",'" + str(amministrativa_dct_amministrativi[1]['adm1_name']).capitalize() + "'," + amministrativa_dct_amministrativi[1]['adm1_code'] +
                             "," + amministrativa_dct_amministrativi[1]['adm2_code'] + ",'" + adm2_amministrativa +
                             "'," + str(amministrativa_dct_inondazione[1][25]) + "," + str(amministrativa_dct_inondazione[1][50]) +
                             "," + str(amministrativa_dct_inondazione[1][100]) + "," + str(amministrativa_dct_inondazione[1][200]) +
                             "," + str(amministrativa_dct_inondazione[1][500]) + "," + str(amministrativa_dct_inondazione[1][1000]))
    lista_comandi = []
    for linea in linee:
         inserimento = "INSERT INTO " + "public.sparc_annual_pop" + \
                       " (iso3,adm0_name,adm0_code,adm1_name,adm1_code,adm2_code,adm2_name,rp25,rp50,rp100,rp200,rp500,rp1000)" \
                       "VALUES('" + linea + ");"
         lista_comandi.append(inserimento)

    return lista_comandi

def inserisci_valori_dbfs(ritornati_passati):

    conn_insert = psycopg2.connect(connection_string)
    cur_insert = conn_insert.cursor()

    for ritornato in ritornati_passati:
        cur_insert.execute(ritornato)

    conn_insert.commit()
    conn_insert.close()
    cur_insert.close()

paese_ricerca = "Pakistan"

#create_sparc_population_monthly_table()
#lst_mensili = read_monthly_values_country_fromTXT(paese_ricerca)

create_sparc_population_annual_table()
dct_annuali = collect_annual_data_byRP_from_dbf_country(paese_ricerca)
adms = dct_annuali[2].keys()
adms_names = [x.split("_")[1] for x in adms]
inserisci_valori_dbfs(process_dct_annuali(adms_names, dct_annuali[2]))



