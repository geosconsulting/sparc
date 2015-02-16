__author__ = 'fabio.lana'
import datetime as dt
from collections import defaultdict
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np

data_store = []
point_counts = defaultdict(int)
interaction_counts = defaultdict(int)

COUNTRY = "AFG"
ANNO_init = 2012
ANNO_end = 2014

PATH = "c:/data/tools/sparc/conflicts/SPARC_GDELT/test_data/"
last_gdelts_file = PATH + "GDELT.MASTERREDUCEDV2.txt"
test_file = PATH + "out" + COUNTRY + ".txt"

def GDELT_fields(file_name):

    with open(file_name) as f:
        col_names = f.readline().split("\t")

    return col_names

def GDELT_subsetting(file_name, country, start, end):

    with open(file_name) as f:
        next(f)
        for raw_row in f:
            row = raw_row.split("\t")
            anno_corrente = int(row[0][:4])
            print anno_corrente
            if anno_corrente >= int(start) and anno_corrente <= int(end):
                #print raw_row
                actor1 = row[1][:3]
                if actor1 == country:
                    #print actor1
                    data_store.append(raw_row)
    return data_store

def GDELT_coords(data_store):

    for row_corrente in data_store:
        try:
            lat_source = float(row_corrente.split("\t")[9])
            lon_source = float(row_corrente.split("\t")[10])
            lat_target = float(row_corrente.split("\t")[15])
            lon_target = float(row_corrente.split("\t")[16])
            # print lat, lon
            point_counts[(lat_source, lon_source)] += 1
            interaction_counts[((lat_source, lon_source), (lat_target, lon_target))] += 1
        except:
            pass

    return point_counts

def GDELTS_stat(point_counts):

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

def GDELT_maplot(point_counts):

    def get_size(count):
        '''
        Convert a count to a point size.
        Log-scaled.
        '''
        scale_factor = 2
        return np.log10(count + 1) * scale_factor

    # Note that we're drawing on a regular matplotlib figure, so we set the
    # figure size just like we would any other.
    plt.figure(figsize=(12, 12))

    # Create the Basemap
    event_map = Basemap(projection='merc',
                        resolution='l', area_thresh=1000.0,  # Low resolution
                        lat_0=15, lon_0=30,  # Map center
                        llcrnrlon=10, llcrnrlat=1,  # Lower left corner
                        urcrnrlon=50, urcrnrlat=30)  # Upper right corner
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

def GDELT_interactions_maplot():

    max_val = np.log10(counts_int.max())

    def get_alpha(interaction_counts):
        '''
        Convert a count to an alpha val.
        Log-scaled
        '''
        scale = np.log10(interaction_counts)
        return (scale/max_val) * 0.25

    # Draw the basemap like before
    plt.figure(figsize=(12,12))
    event_map = Basemap(projection='merc',
                        resolution='l', area_thresh=1000.0,  # Low resolution
                        lat_0=15, lon_0=30,  # Map center
                        llcrnrlon=10, llcrnrlat=1,  # Lower left corner
                        urcrnrlon=50, urcrnrlat=30)  # Upper right corner
    # Draw important features
    event_map.drawcoastlines()
    event_map.drawcountries()
    event_map.fillcontinents(color='0.8')
    event_map.drawmapboundary()

    # Draw the lines on the map:
    for arc, count in interaction_counts.iteritems():
        point1, point2 = arc
        y1, x1 = point1
        y2, x2 = point2

        # Only plot lines where both points are on our map:
        if ((x1 > 10 and x1 < 100 and y1 > 20 and y1 < 70) and
            (x2 > 10 and x2 < 100 and y2 > 20 and y2 < 70)):

            line_alpha = get_alpha(count)

            # Draw the great circle line
            event_map.drawgreatcircle(x1, y1, x2, y2, linewidth=2,color='r', alpha=line_alpha)

    plt.show()

def file_len(fname):

    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def GDELT_splitting(file_name, country, start, end, n_righe):

    sotto = 0
    sopra = n_righe

    fp = open(file_name)
    next(fp)
    for i, line in enumerate(fp):
        anno_controllo_minimo = int(line.split("\t")[1][:4])
        if i== 0 and start < anno_controllo_minimo:
            print "Fuori range"
            break
        if i == 0:
            anno_minimo = int(line.split("\t")[1][:4])
        elif i == n_righe/2:
            row = line.split("\t")
            anno_corrente = int(row[1][:4])
            if anno_corrente >= start:
                sotto = 0
                sopra = i
            else:
                sotto= n_righe/2
                sopra = n_righe
        # elif i == n_righe:
        #     anno_massimo = int(line.split("\t")[1][:4])

    fp.close()

    return anno_minimo, sotto, sopra

def main():

    #n_righe = file_len(test_file)
    #print("Ci sono %d linee di testo" % n_righe)

    #anno_min,lim_inf,lim_sup = GDELT_splitting(test_file,COUNTRY, ANNO_init, ANNO_end, n_righe)
    #print("Nel file l'anno minimo e' %d.\n L'anno di ricerca si trova tra le linee %d - %d" % (anno_min,lim_inf,lim_sup))

    #GDELT_fields(last_gdelts_file)
    GDELT_subsetting(last_gdelts_file, COUNTRY, ANNO_init, ANNO_end)
    #data_store = GDELT_subsetting(test_file, COUNTRY, ANNO_init, ANNO_end)
    #punti = GDELT_coords(data_store)
    #print punti
    #linee = calcolo.GDELT_coords(data_store)[1]
    #print GDELTS_stat(punti)
    #GDELT_maplot(punti)
    #GDELT_interactions_maplot()

if __name__ == "__main__":
     main()