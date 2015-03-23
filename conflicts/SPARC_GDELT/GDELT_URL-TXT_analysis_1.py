__author__ = 'fabio.lana'

import requests
import lxml.html as lh
import urllib
import zipfile
import os
import numpy as np
import pandas as pd
import pandas.io.sql as psql
import datetime as dt
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

from sqlalchemy import create_engine
from collections import defaultdict

gdelt_base_url = 'http://data.gdeltproject.org/events/'
headers_daily = "CSV.header.dailyupdates.txt"
headers_historical = "CSV.header.historical.txt"
PATH = "c:/data/tools/sparc/conflicts/SPARC_GDELT/test_data/"

########## WEB SCRAPING #############
def gdelt_day_month_year():

    # get the list of all the links on the gdelt file page
    page = requests.get(gdelt_base_url + 'index.html')
    doc = lh.fromstring(page.content)
    link_list = doc.xpath("//*/ul/li/a/@href")

    # separate out those links that begin with four digits
    list_days = [x for x in link_list if len(x) == 23]
    list_months = [x for x in link_list if len(x) == 10]
    list_years = [x for x in link_list if len(x) == 8]

    return list_days, list_months, list_years

def gdelt_latest(data_minima, data_massima):

    # get the list of all the links on the gdelt file page
    page = requests.get(gdelt_base_url + 'index.html')
    doc = lh.fromstring(page.content)
    link_list = doc.xpath("//*/ul/li/a/@href")

    # separate out those links that begin with four digits
    latest = [x for x in link_list if str.isdigit(x[0:8]) and (x[0:8]>= str(data_minima) and x[0:8] <= str(data_massima))]

    return latest

########## COPIARE IN DB #############
def deal_with_db(gdelts_file):

    print gdelts_file
    nome = gdelts_file.split("/")[8].split(".")[0]
    print nome

    colnames = pd.read_excel('../SPARC_GDELT/CSV.header.fieldids_hist.xlsx', sheetname='Sheet1',
                             index_col='Column ID', parse_cols=1)['Field Name']

    # Build DataFrames from each of the intermediary files
    DF_annuale = pd.read_csv(gdelts_file, sep='\t', header=None, dtype=str, names=colnames,
                             index_col=['GLOBALEVENTID'])

    engine = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports')
    connection = engine.connect()

    DF_annuale.to_sql('gd_' + str(nome), engine, schema='conflicts', chunksize=1000)

    connection.close()

def deal_with_db_iterative(gdelts_file_csv):

    print gdelts_file_csv
    nome = gdelts_file_csv.split("/")[8].split(".")[0]
    print nome

    chunksize = 1000 # number of lines to process at each iteration

    import csv
    # Get number of lines in the CSV file
    nlines = sum(1 for row in csv.reader(open(gdelts_file_csv)))

    colnames = pd.read_excel('../SPARC_GDELT/CSV.header.fieldids_hist.xlsx', sheetname='Sheet1',
                             index_col='Column ID', parse_cols=1)['Field Name']

    engine = create_engine('postgresql://geonode:geonode@localhost/geonode-imports')
    connection = engine.connect()

    # Iteratively read CSV and dump lines into the SQLite table
    for i in range(0, nlines, chunksize):

        df_chunks = pd.read_csv(gdelts_file_csv,
                                sep='\t',
                                header=None,
                                nrows=chunksize,
                                skiprows=i,
                                dtype=str,
                                names=colnames,
                                index_col=['GLOBALEVENTID'])

        if (i==0):
            print df_chunks[2:][:3]

        if (i==1000):
            print df_chunks[:2][:3]

        if (i==2000):
            print df_chunks[:2][:3]

        # psql.to_sql(df_chunks,
        #             name = 'gd_' + str(nome),
        #             con = engine,
        #             schema='conflicts',
        #             if_exists='append')

    connection.close()

########## LEGGERE DA DB  #############
def fetch_data(anno):

    engine = create_engine('postgresql://geonode:geonode@localhost/geonode-imports')
    connection = engine.connect()

    from sqlalchemy.orm import sessionmaker, scoped_session
    conta_sql = "SELECT COUNT (*) FROM conflicts.gd_" + str(anno) + ";"
    Session = scoped_session(sessionmaker(bind=engine))
    s = Session()
    num_records = list(s.execute(conta_sql))[0][0]
    #print num_records

    stringa_sql = 'SELECT "SQLDATE","Actor1Code","GoldsteinScale" FROM conflicts.gd_' + str(anno) + ';'
    #stringa_sql = "SELECT * FROM sparc_wfp_areas;"
    #print stringa_sql

    df = psql.read_sql_query(stringa_sql, con=engine)
    #print df.columns.values
    #print df.describe()
    connection.close()

    return df

def gdelt_scompatta(file_list):

    infilecounter = 0

    for compressed_file in file_list[infilecounter:]:
        print compressed_file,
        # if we dont have the compressed file stored locally, go get it. Keep trying if necessary.
        while not os.path.isfile(PATH + compressed_file):
            print 'downloading,',
            urllib.urlretrieve(url=gdelt_base_url + compressed_file,
                               filename=PATH + compressed_file)

        # extract the contents of the compressed file to a temporary directory
        print 'extracting,',
        z = zipfile.ZipFile(file=PATH + compressed_file, mode='r')
        z.extractall(path= PATH + 'tmp/')

        # parse each of the csv files in the working directory,
        print 'parsing,',
        infile_name = PATH + "tmp/" + compressed_file.split(".")[0] + ".csv"
            # open the infile and outfile
        #with open(infile_name, mode='r') as infile:
        print infile_name
        deal_with_db(infile_name)
        #delete the temporary file
        os.remove(PATH + compressed_file)
        os.remove(infile_name)
        infilecounter += 1

    return 'done'

def gdelt_pandas_date(returned_df):

    mindata = returned_df['SQLDATE'].min()
    maxdata = returned_df['SQLDATE'].max()

    returned_df['Date'] = pd.Series([pd.to_datetime(date) for date in returned_df['SQLDATE']], index= returned_df.index)
    print returned_df.head()

    #TODO: il campo e'convertito ma adesso devo fare riferimento alle date per plottare le serie
    #TODO: e' solo un problema di indirizzare il campo date ma Pandas e' un casino in questo senso
    #montly_df['ActionGeo_Type'].hist(by=montly_df['date'])
    #plt.show()
    bymonth = returned_df.groupby('Date')
    bygroup_type = returned_df.groupby(['Date', 'ActionGeo_Type'])
    print(bygroup_type.describe())

def GDELT_fields(file_name):

    lista_corrente = []

    with open(file_name) as f:
        col_names = f.readline().split("\t")

    for campo in col_names:
        lista_corrente.append(campo.replace("\n",""))

    return lista_corrente

def genera_liste_giorno_mese_anno():

    lst_storica = GDELT_fields(headers_historical)
    lst_giornaliera = GDELT_fields(headers_daily)

    print("La lista storica ha %d campi mentre la giornaliera ha %d campi" % (len(lst_storica), len(lst_giornaliera)))

    mancante = (list(set(lst_giornaliera) - set(lst_storica)))
    print("Il campo mancante in storica e' %s" % mancante[0])

    giorni, mesi, anni = gdelt_day_month_year()
    print "Ci sono %d files giornalieri %d mensili e %d annuali" % (len(giorni), len(mesi), len(anni))

    return giorni, mesi, anni

def depickle_pandas(paesiuzzo):

    local_path = 'C:/data/tools/sparc/conflicts/SPARC_GDELT/test_data/results/'
    filolo = local_path + paesiuzzo + '.pickle'
    #print filolo
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
    d_trans.to_sql('gd_' + str(paesiuzzo), engine, schema='conflicts', chunksize=1000)
    connection.close()

    return d_trans

def depickle_pandas_current(fips):

        local_path = 'C:/data/tools/sparc/conflicts/SPARC_GDELT/test_data/results/'
        filolo = local_path + 'current_' + fips + '.pickle'
        file_pickle = pd.io.pickle.read_pickle(filolo)

        # Get the GDELT field names from a helper file
        colnames = pd.read_excel('CSV.header.fieldids.xlsx', sheetname='Sheet1',
                                 index_col='Column ID', parse_cols=1)['Field Name']

        #df = pd.DataFrame(data= file_pickle, columns=colnames)
        df = pd.DataFrame(data= file_pickle)

        engine = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports')

        connection = engine.connect()
        df.to_sql('gd_' + str(fips), engine, schema='conflicts', chunksize=1000,if_exists='append')
        connection.close()

        return df

def chart_from_masterReduced():

    monthly_data = defaultdict(int)  # We'll use this to store the counts
    count = 0  # While we're at it, let's count how many records there are, total.
    for year in range(1979, 2013):
        # print year # Uncomment this line to see the program's progress.
        f = open(PATH + "manuali/GDELT.MASTERREDUCEDV2.txt")
        next(f)  # Skip the header row.
        for raw_row in f:
            try:
                row = raw_row.split("\t")
                # Get the date, which is in YYYYMMDD format:
                date_str = row[0]
                year = int(date_str[:4])
                month = int(date_str[4:6])
                date = dt.datetime(year, month, 1)
                monthly_data[date] += 1
                count += 1
            except:
                pass  # Skip error-generating rows for now.
    print "Total rows processed:", count
    print "Total months:", len(monthly_data)
    monthly_events = pd.Series(monthly_data)
    monthly_events.plot()

def analizziamo_dati():

    engine = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports')
    connection = engine.connect()
    sql = 'SELECT "Quad* FROM conflicts."gd_Kyrgyzstan" WHERE "Actor1Name" = \'ACTIVIST\';'
    analisi = psql.read_sql(sql, engine)
    connection.close()

    return analisi

def main():

    pass
    ######## PICKLE CREATI CON INTERFACCIA ########
    #depickle_pandas('South Sudan')
    #depickle_pandas_current('OD')

    #print depickle_pandas('Kyrgyzstan')[0][0]
    #print depickle_pandas('Kyrgyzstan')[12]

    ######## LISTA DEI FILES CSV DISPONIBILI NEL SITO GDELT ########
    #anni = genera_liste_giorno_mese_anno()[2]
    #mesi = genera_liste_giorno_mese_anno()[1]
    #gdelt_scompatta(mesi)

    ######## CALCOLO ########
    ########################
    #57 campi ANNUALI

    #in una passata
    #annual_gdelts_file = PATH + "manuali/1979.csv"

    #da splitare
    #annual_gdelts_file = PATH + "manuali/2005.csv"

    #Un file tutto insieme
    #deal_with_db(annual_gdelts_file)

    #Un file da splittare
    #deal_with_db_iterative(annual_gdelts_file)

    ########################
    #58 campi MENSILI
    #daily_gdelts_file = PATH + "20150106.export.csv"

    ############## CHARTARE I DATI ###############
    #chart_from_masterReduced()

if __name__ == "__main__":
    main()

ritornati = analizziamo_dati()
ritornati['data_conv'] = pd.Series([pd.to_datetime(date) for date in ritornati['SQLDATE']], index=ritornati.index)
# ritornati['mesi'] = ritornati['MonthYear'].str[4:]
#
# print ritornati.head()
# #print ritornati.mesi.head()
#
# ts = pd.Series(ritornati['ActionGeo_Type'])
# print ts.head()
#
# raggruppati = ritornati.groupby('mesi').count()
# ts1= raggruppati['ActionGeo_Type']
# print ts1