__author__ = 'fabio.lana'

import requests
import lxml.html as lh
import urllib
import zipfile
import glob
import operator
import os
import pandas as pd
import shapefile

gdelt_base_url = 'http://data.gdeltproject.org/events/'
local_path = 'c:/data/tools/conflicts/GDELT_Data/'
fips_country_code = 'SU'

def gdelt_connect():

    # get the list of all the links on the gdelt file page
    page = requests.get(gdelt_base_url + 'index.html')
    doc = lh.fromstring(page.content)
    link_list = doc.xpath("//*/ul/li/a/@href")

    # separate out those links that begin with four digits
    file_list = [x for x in link_list if str.isdigit(x[0:4]) and (x[0:4]=='2015')]
    return file_list

def gdelt_country(file_list):

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

def gdelt_pandas_conversion():

    # Get the GDELT field names from a helper file
    colnames = pd.read_excel('CSV.header.fieldids.xlsx', sheetname='Sheet1',
                             index_col='Column ID', parse_cols=1)['Field Name']

    # Build DataFrames from each of the intermediary files
    files = glob.glob(local_path + 'country/'+ fips_country_code + '*')
    files_zips = glob.glob(local_path + '*.zip')
    DFlist = []
    for active_file in files:
        print active_file
        DFlist.append(pd.read_csv(active_file, sep='\t', header=None, dtype=str,
                                  names=colnames, index_col=['GLOBALEVENTID']))

    # Merge the file-based dataframes and save a pickle
    DF = pd.concat(DFlist)
    DF.to_pickle(local_path + 'results/' + 'backup' + fips_country_code + '.pickle')

    # once everything is safely stored away, remove the temporary files
    for active_file in files:
        os.remove(active_file)

    for active_zip in files_zips:
        os.remove(active_zip)

    return DF

# lista_zip = gdelt_connect()
# gdelt_country(lista_zip)
# gdelt_pandas_conversion()
tabella_gdelt =  pd.io.pickle.read_pickle(local_path + 'results/' + 'backup' + fips_country_code + '.pickle')

tabella_gdelt.to_csv("illo.csv")
#print tabella_gdelt.describe()

df = tabella_gdelt[['Year','Actor1Name','Actor1Geo_FullName','Actor2Geo_Lat','Actor2Geo_Long']]
df = df.dropna()
#print df.head()

out_file = 'GDELT' + fips_country_code + '.shp'

w = shapefile.Writer(shapefile.POINT)
w.autoBalance = 1 #ensures geometry and attributes match
w.field('id','F',15,0)

for illo in range(0,len(df)):
    coords = df.iloc[illo][3:5]
    print df.index[illo],coords[0],coords[1]
    w.point(float(coords[0]),float(coords[1]))
    w.record(df.index[illo])

#Save shapefile
w.save(out_file)









