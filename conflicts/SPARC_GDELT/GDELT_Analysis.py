__author__ = 'fabio.lana'

from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd
import shapefile

gdelt_base_url = 'http://data.gdeltproject.org/events/'
local_path = '../SPARC_GDELT/GDELT_Data/'
PATH = '../SPARC_GDELT/test_data/'

class GDELT_Analysis(object):

    def depickle_current(self,tempo, paese):
        local_path = 'C:/data/tools/sparc/conflicts/SPARC_GDELT/test_data/results/'
        filolo = local_path + tempo + '_' + paese + '.pickle'
        file_pickle = pd.io.pickle.read_pickle(filolo)

        # Get the GDELT field names from a helper file
        colnames = pd.read_excel('CSV.header.fieldids.xlsx', sheetname='Sheet1',
                                 index_col='Column ID', parse_cols=1)['Field Name']

        #df = pd.DataFrame(data= file_pickle, columns=colnames)
        df = pd.DataFrame(data= file_pickle)

        df['Date'] = pd.Series([pd.to_datetime(date) for date in df['SQLDATE']], index= df.index)
        df['Year'] = pd.DatetimeIndex(df['Date']).year
        df['Month'] = pd.DatetimeIndex(df['Date']).month
        df['Day'] = pd.DatetimeIndex(df['Date']).day

        return df

    def chart_country(self,tabella_gdelt):

        pivot = pd.pivot_table(tabella_gdelt, values="SQLDATE", index=["Date"], columns=["QuadClass"], aggfunc=len)
        pivot = pivot.fillna(0) # Replace any missing data with zeros

        # Now we no longer need the Year and Month columns, so let's drop them:
        pivot = pivot[["1", "2", "3", "4"]]
        # Rename the QuadCat columns
        pivot = pivot.rename(columns={"1": "Material Cooperation",
                                      "2": "Verbal Cooperation",
                                      "3": "Verbal Conflict",
                                      "4": "Material Conflict"})
        pivot.plot(figsize=(12, 6))
        plt.show()

    def gdelt_country_gis_file(self,tabella_gdelt, paese):

        df = tabella_gdelt[['Year', 'Actor1Name', 'Actor1Geo_FullName', 'Actor2Geo_Lat', 'Actor2Geo_Long']]
        df = df.dropna()
        print df.head()
        out_file = 'test_data/shps/' + paese + '.shp'
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


