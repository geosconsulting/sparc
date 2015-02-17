__author__ = 'fabio.lana'

import requests
import lxml.html as lh
import urllib
import zipfile
import glob
import operator
import os
import shapefile
import datetime as dt
from collections import defaultdict
import numpy as np
import pandas as pd

import GDELT_DB as gdb

gdelt_base_url = 'http://data.gdeltproject.org/events/'
local_path = '../SPARC_GDELT/GDELT_Data/'
file = 'out.txt'

headers_daily = "CSV.header.dailyupdates.txt"
headers_historical = "CSV.header.historical.txt"
PATH = "c:/data/tools/sparc/conflicts/SPARC_GDELT/test_data/"

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

def gdelt_pandas_date(returned_df):

    mindata = returned_df['SQLDATE'].min()
    maxdata = returned_df['SQLDATE'].max()

    returned_df['Date'] = pd.Series([pd.to_datetime(date) for date in returned_df['SQLDATE']],index= returned_df.index)
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

genera_liste_giorno_mese_anno()

######## CALCOLO ########

#57 campi
annual_gdelts_file = PATH + "1979.csv"
monthly_gdelts_file = PATH + "200901.csv"

#58 campi
daily_gdelts_file = PATH + "20150106.export.csv"

colnames = pd.read_excel('../SPARC_GDELT/CSV.header.fieldids_hist.xlsx', sheetname='Sheet1',
                             index_col='Column ID', parse_cols=1)['Field Name']

# Build DataFrames from each of the intermediary files
DF_annuale = pd.read_csv(annual_gdelts_file, sep='\t', header=None, dtype=str, names=colnames, index_col=['GLOBALEVENTID'])
print DF_annuale.describe()

host = 'localhost'
schema = 'public'
dbname = 'geonode-imports'
user = 'geonode'
password = 'geonode'
table = 'sparc_gdelt_archive'

objDB = gdb.GDELT_DB(host, schema, dbname, user, password)
