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
import scipy as sp
import matplotlib.pyplot as plt

gdelt_base_url = 'http://data.gdeltproject.org/events/'
local_path = '../SPARC_GDELT/GDELT_Data/'
PATH = '../SPARC_GDELT/test_data/'
file = 'out.txt'

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

def gdelt_country(file_list,fips_country_code):

    infilecounter = 0
    outfilecounter = 0

    for compressed_file in file_list[infilecounter:]:
        print compressed_file,

        # if we dont have the compressed file stored locally, go get it. Keep trying if necessary.
        while not os.path.isfile(local_path+compressed_file):
            print 'downloading,',
            urllib.urlretrieve(url= gdelt_base_url + compressed_file,
                               filename=local_path+compressed_file)

        # extract the contents of the compressed file to a temporary directory
        print 'extracting,',
        z = zipfile.ZipFile(file=local_path + compressed_file, mode='r')
        z.extractall(path=local_path + 'tmp/')

        # parse each of the csv files in the working directory,
        print 'parsing,',
        for infile_name in glob.glob(local_path + 'tmp/*'):
            outfile_name = local_path + 'country/' + fips_country_code + '%04i.tsv'%outfilecounter
            print outfile_name
            # open the infile and outfile
            with open(infile_name, mode='r') as infile, open(outfile_name, mode='w') as outfile:
                for line in infile:
                    # extract lines with our interest country code
                    if fips_country_code in operator.itemgetter(51, 37, 44)(line.split('\t')):
                        outfile.write(line)
                outfilecounter +=1

            # delete the temporary file
            os.remove(infile_name)
        infilecounter +=1
    print 'done'

    return infilecounter

def gdelt_pandas_conversion(fips_country_code):

    # Get the GDELT field names from a helper file
    colnames = pd.read_excel('../SPARC_GDELT/CSV.header.fieldids.xlsx', sheetname='Sheet1',
                             index_col='Column ID', parse_cols=1)['Field Name']

    # Build DataFrames from each of the intermediary files
    files = glob.glob(local_path + 'country/' + fips_country_code + '*')

    DFlist = []
    for active_file in files:
        DFlist.append(pd.read_csv(active_file, sep='\t', header=None, dtype=str,
                                  names=colnames, index_col=['GLOBALEVENTID']))

    # Merge the file-based dataframes and save a pickle
    DF = pd.concat(DFlist)

    #AL MOMENTO NON LO SALVO COME PICKLE FORSE RISPARMIO TEMPO
    #DF.to_pickle(local_path + 'results/' + 'backup' + fips_country_code + '.pickle')

    # once everything is safely stored away, remove the temporary files
    for active_file in files:
        os.remove(active_file)

    files_zips = glob.glob(local_path + '*.zip')
    for active_zip in files_zips:
        os.remove(active_zip)

    return DF

def gdelt_country_gis_file(fips_country_code):

    tabella_gdelt = pd.io.pickle.read_pickle(local_path + 'results/' + 'backup' + fips_country_code + '.pickle')

    print tabella_gdelt.describe()
    df = tabella_gdelt[['Year', 'Actor1Name', 'Actor1Geo_FullName', 'Actor2Geo_Lat', 'Actor2Geo_Long']]
    df = df.dropna()
    print df.head()
    out_file = 'GDELT' + fips_country_code + '.shp'
    w = shapefile.Writer(shapefile.POINT)
    w.autoBalance = 1  # ensures geometry and attributes match
    w.field('id', 'F', 15, 0)
    for illo in range(0, len(df)):
        coords = df.iloc[illo][3:5]
        print df.index[illo], coords[0], coords[1]
        w.point(float(coords[0]), float(coords[1]))
        w.record(df.index[illo])

    # Save shapefile
    w.save(out_file)

def gdelt_country_chart_txt_file(fips_country_code):

    monthly_data = defaultdict(int) # We'll use this to store the counts
    count = 0 # While we're at it, let's count how many records there are, total.

    for year in range(1979, 2013):
        #print year # Uncomment this line to see the program's progress.
        f = open(PATH + file)
        next(f) # Skip the header row.
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
                pass # Skip error-generating rows for now.

    print "Total rows processed:", count
    print "Total months:", len(monthly_data)
    #print monthly_data
    return monthly_data

def gdelt_stat(tornanti):

    # Get some summary statistics
    counts = np.array(tornanti.values())
    #global counts_int
    #counts_int = np.array(interaction_counts.values())

    statistiche = {}
    statistiche["Total points:"] = len(counts)
    #statistiche["Total point-pairs:"] = len(counts_int)
    statistiche["Min events:"] = counts.min()
    statistiche["Max events:"] = counts.max()
    statistiche["Mean events:"] = counts.mean()
    statistiche["Median points:"] = np.median(counts)
    return statistiche

def gdelt_country_chart_pandas(returned_df):

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

######## CALCOLO ########
giorni, mesi, anni = gdelt_day_month_year()
print "Ci sono %d files giornalieri %d mensili e %d annuali" % (len(giorni), len(mesi), len(anni))

fips_country_code = 'AF'
now = dt.datetime.now()
meno_3 = dt.timedelta(days=3)
mese_passato = now - meno_3

massimo = now.strftime("%Y%m%d")
minimo = mese_passato.strftime("%Y%m%d")
print("Between %s and %s" % (str(massimo), str(minimo)))

lista_files = gdelt_latest(minimo, massimo)
print("Found %d files\n" % len(lista_files))

# esito = gdelt_country(lista_files, fips_country_code)
# montly_df = gdelt_pandas_conversion(fips_country_code)
# campi = list(montly_df.columns.values)
# gdelt_country_chart_pandas(montly_df)

# monthly_data = gdelt_country_chart_txt_file(fips_country_code)
# monthly_events = pd.Series(monthly_data)
# monthly_events.plot()
# plt.show()