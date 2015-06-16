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
local_path = 'C:/data/tools/sparc/conflicts/SPARC_GDELT/test_data/'
#fips_country_code = 'SU'

url_files = gdelt_base_url
down_files = local_path + 'down/'
temp_files = local_path + 'tmp/'
country_files = local_path + 'country/'

class GDELT_Fetch(object):

    def collect_file_list(self, data_minima, data_massima):

        # get the list of all the links on the gdelt file page
        page = requests.get(gdelt_base_url + 'index.html')
        doc = lh.fromstring(page.content)
        link_list = doc.xpath("//*/ul/li/a/@href")

        #troviamo i files che corrispondono alla lista settimanale
        file_list = [x for x in link_list if str.isdigit(x[0:8]) and (x[0:8] >= str(data_minima) and x[0:8] <= str(data_massima))]

        return file_list

    #DA RIMUOVERE
    def gdelt_connect(self, data_minima, data_massima):

        # get the list of all the links on the gdelt file page
        page = requests.get(gdelt_base_url + 'index.html')
        doc = lh.fromstring(page.content)
        link_list = doc.xpath("//*/ul/li/a/@href")

        # separate out those links that begin with four digits
        file_list = [x for x in link_list if str.isdigit(x[0:4]) and (x[0:4] >= str(data_minima) and x[0:4] <= str(data_massima))]

        return file_list

    def download_process_delete(self, file_list, fips_country_code):

        infilecounter = 0
        outfilecounter = 0

        print file_list

        for compressed_file in file_list[infilecounter:]:

            print compressed_file,
            # if we dont have the compressed file stored locally, go get it. Keep trying if necessary.
            while not os.path.isfile(down_files + compressed_file):
                print 'downloading,',
                urllib.urlretrieve(url=url_files + compressed_file,
                                   filename=down_files + compressed_file)

            # extract the contents of the compressed file to a temporary directory
            print 'extracting,',
            z = zipfile.ZipFile(file= down_files + compressed_file, mode='r')
            z.extractall(path=temp_files)
            #z.close()
            #os.remove(down_files + compressed_file)

            # parse each of the csv files in the working directory,
            print 'parsing,',
            for infile_name in glob.glob(temp_files + '/*'):
                outfile_name = country_files + fips_country_code + '%04i.tsv' % outfilecounter
                print outfile_name
                # open the infile and outfile
                with open(infile_name, mode='r') as infile, open(outfile_name, mode='w') as outfile:
                    for line in infile:
                        # extract lines with our interest country code
                        if fips_country_code in operator.itemgetter(51, 37, 44)(line.split('\t')):
                            outfile.write(line)
                    outfilecounter += 1
                # delete the temporary file
                os.remove(infile_name)
            infilecounter += 1

        #files_zips = glob.glob(down_files + '*.zip')
        #for active_zip in files_zips:
            #os.remove(active_zip)

        return 'done'

    def gdelt_pandas_conversion(self, fips_country_code,paese, temporal):

        # Get the GDELT field names from a helper file
        colnames = pd.read_excel('CSV.header.fieldids.xlsx', sheetname='Sheet1',
                                 index_col='Column ID', parse_cols=1)['Field Name']

        # Build DataFrames from each of the intermediary files
        files = glob.glob(local_path + 'country/' + fips_country_code + '*')
        files_zips = glob.glob(local_path + 'country/' + '*.zip')
        DFlist = []
        for active_file in files:
            print active_file
            DFlist.append(pd.read_csv(active_file, sep='\t', header=None, dtype=str,
                                      names=colnames, index_col=['GLOBALEVENTID']))

        print DFlist
        # Merge the file-based dataframes and save a pickle
        DF = pd.concat(DFlist)
        DF.to_pickle(local_path + 'results/' + temporal +'_' + paese + '.pickle')

        # once everything is safely stored away, remove the temporary files
        for active_file in files:
            os.remove(active_file)

        for active_zip in files_zips:
            os.remove(active_zip)

        return DF

    def convert_2_shapefile(self,fips_country_code):

        # lista_zip = gdelt_connect()
        # gdelt_country(lista_zip)
        # gdelt_pandas_conversion()
        tabella_gdelt = pd.io.pickle.read_pickle(local_path + 'results/' + 'backup' + fips_country_code + '.pickle')
        #tabella_gdelt.to_csv("illo.csv")
        # print tabella_gdelt.describe()
        df = tabella_gdelt[['Year', 'Actor1Name', 'Actor1Geo_FullName', 'Actor2Geo_Lat', 'Actor2Geo_Long']]
        df = df.dropna()
        #print df.head()
        out_file = 'GDELT' + fips_country_code + '.shp'
        w = shapefile.Writer(shapefile.POINT)
        w.autoBalance = 1  #ensures geometry and attributes match
        w.field('id', 'F', 15, 0)
        for illo in range(0, len(df)):
            coords = df.iloc[illo][3:5]
            print df.index[illo], coords[0], coords[1]
            w.point(float(coords[0]), float(coords[1]))
            w.record(df.index[illo])

        #Save shapefile
        w.save(out_file)
