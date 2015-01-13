__author__ = 'fabio.lana'
import psycopg2
from collections import Counter,OrderedDict
import pandas as pd
import numpy as np

schema = 'public'
dbname = 'geonode-imports'
user = 'geonode'
password = 'geonode'
connection_string = "dbname=%s user=%s password=%s" % (dbname, user, password)
direttorio_radice = "C:/data/tools/sparc/projects/"

def lista_aree_amministrative(paese_ricerca):

    conn_check = psycopg2.connect(connection_string)
    cur_check = conn_check.cursor()

    comando = "SELECT adm0_name,adm2_code,adm2_name FROM sparc_month_prec_norm WHERE adm0_name = '" + paese_ricerca.title() + "';"
    #comando = "SELECT adm0_name,adm2_code,adm2_name FROM sparc_month_prec_norm WHERE adm0_name = 'Lao PDR';"
    print comando
    cur_check.execute(comando);

    lista_admin = []

    for row in cur_check:
        lista_admin.append(row)

    cur_check.close()
    conn_check.close()

    return lista_admin

def normalizzazione_incidenti_mensili_paese(paese_ricerca):

    conn_check = psycopg2.connect(connection_string)
    cur_check = conn_check.cursor()

    comando = "SELECT * FROM sparc_flood_emdat WHERE country = '" + paese_ricerca.title() + "';"
    #comando = "SELECT * FROM sparc_flood_emdat WHERE country = 'Lao PDR';"
    mesi_inizio = []
    mesi_fine = []
    cur_check.execute(comando);
    for row in cur_check:
        mesi_inizio.append(int(str(row[1]).strip().split("-")[1]))
        mesi_fine.append(int(str(row[2]).strip().split("-")[1]))
        #print str(row[10]).strip(),row[2]-row[1]
        #print str(row[10]).strip()
        #adm0_name = str(row[1]).strip()

    cur_check.close()
    conn_check.close()

    conta_mesi_inzio = Counter(mesi_inizio)
    conta_mesi_ord_inzio = OrderedDict(sorted(conta_mesi_inzio.items()))

    conta_mesi_fine = Counter(mesi_fine)
    conta_mesi_ord_fine = OrderedDict(sorted(conta_mesi_fine.items()))

    missing_inizio = []
    missing_fine = []
    for indice in range(1, 13):
        if indice not in conta_mesi_ord_inzio:
             missing_inizio.append(indice)
        if indice not in conta_mesi_ord_fine:
             missing_fine.append(indice)

    for valore_inizio in missing_inizio:
        conta_mesi_ord_inzio[valore_inizio] = 0

    for valore_fine in missing_fine:
        conta_mesi_ord_fine[valore_fine] = 0

    danni_mesi_inzio = OrderedDict(sorted(conta_mesi_ord_inzio.items()))
    danni_mesi_fine = OrderedDict(sorted(conta_mesi_ord_fine.items()))
    return danni_mesi_inzio,danni_mesi_fine

def valori_normalizzati_precipitazione_admin2(adm2_ricerca):

    conn_check = psycopg2.connect(connection_string)
    cur_check = conn_check.cursor()

    comando = 'SELECT jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,"dec" FROM sparc_month_prec_norm WHERE adm2_name = \'' + adm2_ricerca.lower() + '\';'

    cur_check.execute(comando);
    indice = 0
    precipitazioni_mensili = {}
    for row in cur_check:
        precipitazioni_mensili[0] = row[0]
        precipitazioni_mensili[1] = row[1]
        precipitazioni_mensili[2] = row[2]
        precipitazioni_mensili[3] = row[3]
        precipitazioni_mensili[4] = row[4]
        precipitazioni_mensili[5] = row[5]
        precipitazioni_mensili[6] = row[6]
        precipitazioni_mensili[7] = row[7]
        precipitazioni_mensili[8] = row[8]
        precipitazioni_mensili[9] = row[9]
        precipitazioni_mensili[10] = row[10]
        precipitazioni_mensili[11] = row[11]
        indice += 1

    cur_check.close()
    conn_check.close()

    return precipitazioni_mensili

def inserisci(comando):

    conn_insert = psycopg2.connect(connection_string)
    cur_insert = conn_insert.cursor()

    #print comando
    cur_insert.execute(comando)

    conn_insert.commit()
    conn_insert.close()
    cur_insert.close()

with open("C:/data/tools/sparc/projects/DRC.txt") as fileggio:
   paesi = [linea.strip() for linea in fileggio]


for paese in paesi:

    #paese_ricerca = "Angola"
    paese_ricerca = paese.title()
    print "Processando %s " % paese_ricerca

    lista_ritornata = lista_aree_amministrative(paese_ricerca)
    print "Ci sono %d aree amministratice in %s" % ((len(lista_ritornata)), paese_ricerca)

    primo = normalizzazione_incidenti_mensili_paese(paese_ricerca)
    df_date_inizio = pd.DataFrame(dict(primo[0]).items(), columns=['Month', 'Cases'])
    #print df_date_inizio

    valori_normalizzati = (df_date_inizio.Cases - df_date_inizio.Cases.min()) / (df_date_inizio.Cases.max() - df_date_inizio.Cases.min())
    df_valori_normalizzati = pd.DataFrame(valori_normalizzati, columns=['Cases'])
    #print df_valori_normalizzati

    inizio = 0
    for adm in lista_ritornata:

        attivo = adm[2].strip()
        precipi = valori_normalizzati_precipitazione_admin2(attivo)
        df_norm_prec = pd.DataFrame(precipi.items(), columns=['Month', 'MM'])
        #print df_norm_prec

        df_globale = pd.merge(df_date_inizio, df_norm_prec, on='Month')
        df_globale['Norm_Cases'] = df_valori_normalizzati
        print df_globale

        correlazione = df_globale['MM'].corr(df_globale['Norm_Cases'])
        print correlazione
        if np.isnan(correlazione):
            correlazione = 0.00
        #print "Per area amministrativa %s il coeffciente di correlazione e' %.2f" % (attivo,correlazione)

        linea = str(adm[0]).strip() + "','" + str(adm[1]).strip() + "','" + attivo + "'," + str(correlazione)
        #print linea
        inizio += 1
        print "Processando %d record nome %s " % (inizio,attivo)
        inserimento = "INSERT INTO public.sparc_correlation(adm0_name,adm2_code,adm2_name,correlation) VALUES('" + linea + ");"
        inserisci(inserimento)
