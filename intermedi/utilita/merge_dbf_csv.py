__author__ = 'fabio.lana'
import os
import dbf
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import glob

schema = 'public'
dbname = 'geonode-imports'
user = 'geonode'
password = 'geonode'
connection_string = "dbname=%s user=%s password=%s" % (dbname, user, password)
direttorio_radice = "C:/data/tools/sparc/projects/"

def becca_il_dbf(paese_ricerca, adms):

    db_connessione = psycopg2.connect(connection_string)
    db_connessione.cursor_factory = RealDictCursor
    db_cursore = db_connessione.cursor()

    lista = []
    for adm in adms:
        sql = "SELECT DISTINCT iso3, adm0_name, adm0_code, adm1_code,adm1_name, adm2_name, adm2_code FROM sparc_population_month WHERE adm2_name = '" + adm + "' AND adm0_name = '" + paese_ricerca + "';"
        #print sql
        db_cursore.execute(sql);
        risultati = db_cursore.fetchall()
        lista.append(risultati)
    print lista

    dct_valori_amministrativi = {}
    for indice in range(0,len(lista)):
        illo = str(lista[indice][0]['adm2_name'].strip()).lower()
        dct_valori_amministrativi[illo] = {}
        dct_valori_amministrativi[illo]["iso3"] = str(lista[indice][0]['iso3'].strip()).lower()
        dct_valori_amministrativi[illo]["adm0_name"] = str(lista[indice][0]['adm0_name'].strip()).lower()
        dct_valori_amministrativi[illo]["adm0_code"] = str(lista[indice][0]['adm0_code'].strip()).lower()
        dct_valori_amministrativi[illo]["adm1_code"] = str(lista[indice][0]['adm1_code'].strip()).lower()
        dct_valori_amministrativi[illo]["adm1_name"] = str(lista[indice][0]['adm1_name'].strip()).lower()
        dct_valori_amministrativi[illo]["adm2_code"] = str(lista[indice][0]['adm2_code'].strip()).lower()
        dct_valori_amministrativi[illo]["adm2_name"] = str(lista[indice][0]['adm2_name'].strip()).lower()

    #for key,value in dct_valori_amministrativi.items():
    #    print dct_valori_amministrativi[key]['iso3']

    direttorio = direttorio_radice + paese_ricerca
    dct_valori_inondazione_annuale = {}
    for direttorio_principale, direttorio_secondario,file_vuoto in os.walk(direttorio):
        if direttorio_principale != direttorio:
            paese = direttorio_principale.split("/")[5].split("\\")[0]
            admin = direttorio_principale.split(paese)[1][1:]
            files_dbf = glob.glob(direttorio_principale + "/*.dbf")
            for file in files_dbf:
                fileName, fileExtension = os.path.splitext(file)
                if 'stat' in fileName:
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

    lista_rp = [25, 50, 100, 200, 500, 1000]
    for valore in dct_valori_inondazione_annuale.items():
        quanti_rp = len(valore[1].keys())
        if quanti_rp<6:
            for rp in lista_rp:
                if rp not in valore[1].keys():
                    dct_valori_inondazione_annuale[valore[0]][rp] = 0

    linee =[]
    for amministrativa_dct_amministrativi in dct_valori_amministrativi.items():
        adm2_amministrativa = amministrativa_dct_amministrativi[0]
        for amministrativa_dct_inondazione in dct_valori_inondazione_annuale.items():
            if amministrativa_dct_inondazione[0] == adm2_amministrativa:
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

def inserisci(ritornati_passati):

    conn_insert = psycopg2.connect(connection_string)
    cur_insert = conn_insert.cursor()

    for ritornato in ritornati_passati:
        print ritornato
        cur_insert.execute(ritornato)

    conn_insert.commit()
    conn_insert.close()
    cur_insert.close()

def becca_il_csv(paese_ricerca):

    conn_check = psycopg2.connect(connection_string)
    cur_check = conn_check.cursor()

    direttorio = direttorio_radice + paese_ricerca

    linee_comandi_prec = []
    linee_comandi_prec_norm = []

    for direttorio_principale, direttorio_secondario, files in os.walk(direttorio):
        if direttorio_principale != direttorio:
            print direttorio_principale
            paese = direttorio_principale.split("/")[5].split("\\")[0]
            admin = direttorio_principale.split(paese)[1][1:]
            comando = "SELECT iso3,adm0_name,adm0_code,adm1_code,adm2_code FROM sparc_population_month where adm2_name_low = '" + admin.lower() + "' AND adm0_name = '" + paese + "';"
            #print comando
            cur_check.execute(comando);
            for row in cur_check:
                iso = str(row[0])
                adm0_name = str(row[1]).strip()
                adm0_code = str(row[2]).strip()
                adm1_code = str(row[3]).strip()
                adm2_code = str(row[4]).strip()

            #print iso,adm0_name,adm0_code,adm1_code,adm2_code,admin
            for file in files:
                fileName, fileExtension = os.path.splitext(file)
                if fileExtension == '.csv':
                    if fileName.count("_") == 1:
                        file_completo = str(direttorio + "/" + admin + "/" + fileName + ".csv")
                        df_prec = pd.DataFrame.from_csv(file_completo, index_col=0, header=-1)
                        #print df_prec
                        minimo_prec = int(df_prec.min())
                        massimo_prec = int(df_prec.max())
                        #print minimo,massimo
                        if minimo_prec==0 and massimo_prec==0:
                            linea_prec= "0,0,0,0,0,0,0,0,0,0,0,0"
                            linee_comandi_prec.append(iso + "','" + adm0_name + "'," + adm0_code + "," + adm1_code + "," + adm2_code + ",'" + admin + "'," + linea_prec)
                        else:
                            valori_prec = map(list, df_prec.transpose().values)
                            linea_prec= str(valori_prec[0][0]) + "," + str(valori_prec[0][1]) + "," + str(valori_prec[0][2]) + "," + str(valori_prec[0][3]) + "," +\
                               str(valori_prec[0][4]) + "," + str(valori_prec[0][5]) + "," + str(valori_prec[0][6]) + "," + str(valori_prec[0][7]) + "," +\
                               str(valori_prec[0][8]) + "," + str(valori_prec[0][9]) + "," + str(valori_prec[0][10]) + "," + str(valori_prec[0][11])
                        #print linea_prec
                        linee_comandi_prec.append(iso + "','" + adm0_name + "'," + adm0_code + "," + adm1_code + "," + adm2_code + ",'" + admin + "'," + linea_prec)

                    if fileName.count("_") == 2:
                        #print "File precipitazioni normalizzate " + str(fileName)
                        file_completo_norm = str(direttorio + "/" + admin + "/" + fileName + ".csv")
                        df_prec_norm = pd.DataFrame.from_csv(file_completo_norm, index_col=0, header=-1)
                        #print df_prec
                        minimo_prec = int(df_prec_norm.min())
                        massimo_prec = int(df_prec_norm.max())
                        #print minimo,massimo
                        if minimo_prec==0 and massimo_prec==0:
                            linea_prec= "0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0"
                            linee_comandi_prec.append(iso + "','" + adm0_name + "'," + adm0_code + "," + adm1_code + "," + adm2_code + ",'" + admin + "'," + linea_prec)
                        else:
                            valori_prec_norm = map(list,df_prec_norm.transpose().values)
                            linea_prec_norm = str(round(valori_prec_norm[0][0],3)) + "," + str(round(valori_prec_norm[0][1],3)) + "," + str(round(valori_prec_norm[0][2],3)) + "," + str(round(valori_prec_norm[0][3],3)) + "," +\
                                   str(round(valori_prec_norm[0][4],3)) + "," + str(round(valori_prec_norm[0][5],3)) + "," + str(round(valori_prec_norm[0][6],3)) + "," + str(round(valori_prec_norm[0][7],3)) + "," +\
                                   str(round(valori_prec_norm[0][8],3)) + "," + str(round(valori_prec_norm[0][9],3)) + "," + str(round(valori_prec_norm[0][10],3)) + "," + str(round(valori_prec_norm[0][11],3))
                            #print linea_prec_norm
                            linee_comandi_prec_norm.append(iso + "','" + adm0_name + "'," + adm0_code + "," + adm1_code + "," + adm2_code + ",'" + admin + "'," + linea_prec_norm)

    lista_sql_prec = []
    for linea_prec in linee_comandi_prec:
        inserimento_rec = "INSERT INTO public.sparc_month_prec" + \
                           "(iso3,adm0_name,adm0_code,adm1_code,adm2_code,adm2_name,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,dec)" \
                           "VALUES('" + linea_prec + ");"
        lista_sql_prec.append(inserimento_rec)

    lista_sql_prec_norm = []
    for linea_prec_norm in linee_comandi_prec_norm:
        inserimento_rec = "INSERT INTO public.sparc_month_prec_norm" + \
                           "(iso3,adm0_name,adm0_code,adm1_code,adm2_code,adm2_name,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,dec)" \
                           "VALUES('" + linea_prec_norm + ");"
        lista_sql_prec_norm.append(inserimento_rec)

    cur_check.close()
    conn_check.close()

    return lista_sql_prec,lista_sql_prec_norm

def inserisci_csv(ritornati_passati):

    conn_insert = psycopg2.connect(connection_string)
    cur_insert = conn_insert.cursor()

    for ritornato in ritornati_passati:
        #print ritornato
        cur_insert.execute(ritornato)

    conn_insert.commit()
    conn_insert.close()
    cur_insert.close()

with open("C:/data/tools/sparc/projects/DRC.txt") as fileggio_paesi:
    paesi = [linea.strip() for linea in fileggio_paesi]
    for paese in paesi:
        file_ricerca = "C:/data/tools/sparc/projects/" + paese + "/adm2_name.csv"
        with open(file_ricerca) as fileggio:
            adms = [linea.strip() for linea in fileggio]
            #print adms
            ritornati = becca_il_dbf(paese, adms)
        inserisci(ritornati)

# with open("C:/data/tools/sparc/projects/lista_paesi.txt") as fileggio_paesi:
#    paesi = [linea.strip() for linea in fileggio_paesi]
#    for paese in paesi:
#        file_ricerca = "C:/data/tools/sparc/projects/" + paese.lower() + "/adm2_name.csv"
#        with open(file_ricerca) as fileggio:
#         adms = [linea.strip() for linea in fileggio]
#         ritornati = becca_il_dbf(paese.capitalize(), adms)
#     #print(ritornati)
# inserisci(ritornati)

#paese_ricerca = "Bhutan"

def varie_chiamate():
    pass
    # VALORI POPOLAZIONE TEMPO RITORNO
    #VALORI POPOLAZIONE TEMPO RITORNO
    #VALORI POPOLAZIONE TEMPO RITORNO
    # for paese in paesi:
    #     paese_ricerca = paese.title()
    #     print paese_ricerca
    #     ritornati = becca_il_dbf(paese_ricerca)
    #     inserisci(ritornati)
    #VALORI POPOLAZIONE TEMPO RITORNO
    #VALORI POPOLAZIONE TEMPO RITORNO
    #VALORI POPOLAZIONE TEMPO RITORNO
    #for paese in paesi:
    #paese = "Lao PDR"
    #paese_ricerca = paese.title()
    # paese_ricerca = "Iraq"
    # ritornati = becca_il_dbf(paese_ricerca)
    # print ritornati
    #inserisci(ritornati)
    # print paese_ricerca
    # ritornati = becca_il_csv(paese_ricerca)
    # inserisci_csv(ritornati[0])
    # inserisci_csv(ritornati[1])

#varie_chiamate()
