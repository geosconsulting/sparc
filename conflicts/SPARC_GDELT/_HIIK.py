__author__ = 'fabio.lana'
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from collections import defaultdict
from geopy.geocoders import Nominatim
from geopy.geocoders import GeoNames
from osgeo import ogr
ogr.UseExceptions()

data_store = []
point_counts = defaultdict(int)
interaction_counts = defaultdict(int)

def HIIK_coords(data_store,paese):

    pass
    # totali = 0
    # successo = 0
    # insuccesso = 0
    #
    # geocoding_testo = open("c:/data/tools/sparc/input_data/geocoded/text/" + paese + ".txt", "wb+")
    # geocoding_testo_fail = open("c:/data/tools/sparc/input_data/geocoded/text/" + paese + "_fail.txt", "wb+")
    #
    # geocoding_testo.write("id,lat,lon\n")
    # geocoding_testo_fail.write("id,lat,lon\n")
    #
    # for incidente in accidents.iteritems():
    #         for location_non_geocoded in incidente[1]['locations'].iteritems():
    #             totali += 1
    #             posto_attivo = location_non_geocoded[1]
    #             if posto_attivo != 'NoData':
    #                 try:
    #                     print("Geocoding " + posto_attivo)
    #                     location_geocoded = self.geolocator.geocode(posto_attivo, timeout=30)
    #                     if location_geocoded:
    #                         scrittura = posto_attivo + "," + str(location_geocoded.longitude) + "," + str(location_geocoded.latitude) + "\n"
    #                         geocoding_testo.write(scrittura)
    #                         successo += 1
    #                     else:
    #                         geocoding_testo_fail.write(posto_attivo + "," + str(0) + "," + str(0) + "\n")
    #                         insuccesso += 1
    #                 except ValueError as e:
    #                     print e.message
    #     print "Total of %s events with %s successful %s unsuccessful and %d NULL" % (
    #     str(totali), str(successo), str(insuccesso), (totali - successo - insuccesso))
    #     perc = float(successo) / float(totali) * 100.0
    #     print "Percentage %.2f of success" % perc
    #
    # for row_corrente in data_store:
    #     try:
    #         lat_source = float(row_corrente.split("\t")[9])
    #         lon_source = float(row_corrente.split("\t")[10])
    #         # print lat, lon
    #         point_counts[(lat_source, lon_source)] += 1
    #     except:
    #         pass
    #
    #     return point_counts

def HIIK_stat(point_counts):

    # Get some summary statistics
    counts = np.array(point_counts.values())
    
    #global counts_int
    counts_int = np.array(interaction_counts.values())

    statistiche = {}
    statistiche["Total points:"] = len(counts)
    statistiche["Total point-pairs:"] = len(counts_int)
    statistiche["Min events:"] = counts.min()
    statistiche["Max events:"] = counts.max()
    statistiche["Mean events:"] = counts.mean()
    statistiche["Median points:"] = np.median(counts)
    
    return statistiche

def HIIK_maplot(point_counts, centro_lat, centro_lon, llat, llon, ulat, ulon):

    # print point_counts
    # print centro_lat, centro_lon, llat, llon, ulat, ulon
    def get_size(count):
        ''' Convert a count to a point size. Log-scaled.'''
        scale_factor = 2
        return np.log10(count + 1) * scale_factor

    # Note that we're drawing on a regular matplotlib figure, so we set the
    # figure size just like we would any other.
    plt.figure(figsize=(10, 10))

    # Create the Basemap
    event_map = Basemap(projection='merc',
        resolution='l', area_thresh=1000.0,  # Low resolution
        lat_0= centro_lat, lon_0=centro_lon,  # Map center
        llcrnrlon=llon, llcrnrlat=llat,  # Lower left corner
        urcrnrlon=ulon, urcrnrlat=ulat)  # Upper right corner

    # Draw important features
    event_map.drawcoastlines()
    event_map.drawcountries()
    event_map.fillcontinents(color='0.8')  # Light gray
    event_map.drawmapboundary()

    # Draw the points on the map:
    for point, count in point_counts.iteritems():
        x, y = event_map(point[1], point[0])  # Convert lat, long to y,x
        # print x , y
        marker_size = get_size(count)
        event_map.plot(x, y, 'ro', markersize=marker_size, alpha=0.3)

    plt.show()

xls_file = r"C:\data\tools\sparc\conflicts\docs\Kevin\rmi_southsudan final.xls"
xls_pd = pd.ExcelFile(xls_file)
df_paese = pd.DataFrame(xls_pd.parse())
print df_paese.head()

