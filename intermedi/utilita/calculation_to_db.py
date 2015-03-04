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

def lista_dbf_paese(paese_ricerca):

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
        #contatore_no += 1
        #lista_no_dbf.add(direttorio_principale)


    lista_stat_dbf = [25, 50, 100, 200, 500, 1000]
    for valore in dct_valori_inondazione_annuale.items():
        quanti_rp = len(valore[1].keys())
        if quanti_rp<6:
            for rp in lista_stat_dbf:
                if rp not in valore[1].keys():
                    dct_valori_inondazione_annuale[valore[0]][rp] = 0

    return contatore_si, lista_si_dbf, dct_valori_inondazione_annuale

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

paese_ricerca = "Pakistan"
dct_valori_tempi_ritorno_zonal_statistic = lista_dbf_paese(paese_ricerca)
# print dct_valori_tempi_ritorno_zonal_statistic[0]
# print dct_valori_tempi_ritorno_zonal_statistic[1]
# print dct_valori_tempi_ritorno_zonal_statistic[2]
for adm,vals in dct_valori_tempi_ritorno_zonal_statistic[2].iteritems():
    print adm,vals


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
