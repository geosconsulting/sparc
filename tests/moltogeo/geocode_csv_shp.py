__author__ = 'fabio.lana'

import csv
import os
from geopy.geocoders import Nominatim
from geopy.geocoders import GeoNames
import shapefile
from osgeo import ogr
ogr.UseExceptions()

class GeocodeCsv(object):

    def __init__(self, paese):
        self.paese = paese
        self.historical_table = "C:/data/tools/sparc/input_data/historical_data/floods - refine.csv"
        self.geolocator = Nominatim()
        self.geolocator_geonames = GeoNames(country_bias = self.paese, username='fabiolana', timeout=1)

    def geolocate_accidents(self):

        accidents = {}
        with open(self.historical_table, 'rb') as csvfile:
            luoghi_splittati = csv.reader(csvfile, delimiter=",", quotechar='"')
            for row in luoghi_splittati:
                if row[2] == self.paese:
                    id_incidente = str(row[9])
                    accidents[id_incidente] = {}
                    accidents[id_incidente]['paese'] = str(row[2])
                    accidents[id_incidente]['killed'] = str(row[6])
                    accidents[id_incidente]['affected'] = str(row[7])
                    accidents[id_incidente]['locations'] = {}
                    gruppo = str(row[3]).split(",")
                    quante_locations = len(gruppo)
                    for i in range(0, quante_locations):
                            accidents[id_incidente]['locations'][i] = gruppo[i].strip()

        totali = 0
        successo = 0
        insuccesso = 0

        geocoding_testo = open("c:/data/tools/sparc/input_data/geocoded/text/" + self.paese + ".txt", "wb+")
        geocoding_testo_fail = open("c:/data/tools/sparc/input_data/geocoded/text/" + self.paese + "_fail.txt", "wb+")

        geocoding_testo.write("id,lat,lon\n")
        geocoding_testo_fail.write("id,lat,lon\n")

        for incidente in accidents.iteritems():
            for location_non_geocoded in incidente[1]['locations'].iteritems():
                totali += 1
                posto_attivo = location_non_geocoded[1]
                if posto_attivo != 'NoData':
                    try:
                        print("Geocoding " + posto_attivo)
                        location_geocoded = self.geolocator.geocode(posto_attivo, timeout=30)
                        if location_geocoded:
                            scrittura = posto_attivo + "," + str(location_geocoded.longitude) + "," + str(location_geocoded.latitude) + "\n"
                            geocoding_testo.write(scrittura)
                            successo += 1
                        else:
                            geocoding_testo_fail.write(posto_attivo + "," + str(0) + "," + str(0) + "\n")
                            insuccesso += 1
                    except ValueError as e:
                        print e.message
        print "Total of %s events with %s successful %s unsuccessful and %d NULL" % (
        str(totali), str(successo), str(insuccesso), (totali - successo - insuccesso))
        perc = float(successo) / float(totali) * 100.0
        print "Percentage %.2f of success" % perc

    def create_validated_coords(self):

        def calc_poligono_controllo():

            poligono = sf.bbox
            global poligono_controllo
            poligono_controllo = ((poligono[2],poligono[1]), (poligono[2],poligono[3]), (poligono[0],poligono[3]), (poligono[0],poligono[1]))
            global n
            n = len(poligono_controllo)

        def punti_dentro_poligono_di_controllo(x,y):

            inside = False

            p1x, p1y = poligono_controllo[0]
            for i in range(n + 1):
                p2x, p2y = poligono_controllo[i % n]
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y
            return inside

        def extract_country_shp():

            # Get the input Layer
            inShapefile = "C:/data/tools/sparc/input_data/gaul/gaul_wfp_iso.shp"
            inDriver = ogr.GetDriverByName("ESRI Shapefile")
            inDataSource = inDriver.Open(inShapefile, 0)
            inLayer = inDataSource.GetLayer()
            print "ADM0_NAME = '" + self.paese + "'"
            inLayer.SetAttributeFilter("ADM0_NAME = '" + self.paese + "'")
            # Create the output LayerS
            outShapefile = "C:/data/tools/sparc/input_data/countries/" + self.paese + ".shp"
            outDriver = ogr.GetDriverByName("ESRI Shapefile")

            # Remove output shapefile if it already exists
            if os.path.exists(outShapefile):
                outDriver.DeleteDataSource(outShapefile)

            # Create the output shapefile
            outDataSource = outDriver.CreateDataSource(outShapefile)
            out_lyr_name = os.path.splitext(os.path.split(outShapefile)[1])[0]
            outLayer = outDataSource.CreateLayer(out_lyr_name, geom_type=ogr.wkbMultiPolygon)

            # Add input Layer Fields to the output Layer if it is the one we want
            inLayerDefn = inLayer.GetLayerDefn()
            for i in range(0, inLayerDefn.GetFieldCount()):
                fieldDefn = inLayerDefn.GetFieldDefn(i)
                fieldName = fieldDefn.GetName()
                print fieldName
                outLayer.CreateField(fieldDefn)

            # Get the output Layer's Feature Definition
            outLayerDefn = outLayer.GetLayerDefn()
            # Add features to the ouput Layer
            for inFeature in inLayer:
                # Create output Feature
                outFeature = ogr.Feature(outLayerDefn)

                # Add field values from input Layer
                for i in range(0, outLayerDefn.GetFieldCount()):
                    fieldDefn = outLayerDefn.GetFieldDefn(i)
                    fieldName = fieldDefn.GetName()
                    outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(),                    inFeature.GetField(i))

                # Set geometry as centroid
                geom = inFeature.GetGeometryRef()
                outFeature.SetGeometry(geom.Clone())
                # Add new feature to output Layer
                outLayer.CreateFeature(outFeature)

            # Close DataSources
            inDataSource.Destroy()
            outDataSource.Destroy()


        dentro = 0
        fuori = 0

        coords_check_file_in = "c:/data/tools/sparc/input_data/geocoded/text/" + self.paese + ".txt"
        coords_validated_file_out = str('c:/data/tools/sparc/input_data/geocoded/csv/' + str(self.paese) + '.csv')

        if os.path.exists("C:/data/tools/sparc/input_data/countries/" + self.paese + ".shp"):
            sf = shapefile.Reader("C:/data/tools/sparc/input_data/countries/" + self.paese + ".shp")
            calc_poligono_controllo()
        else:
            print "Devo estrarre"
            extract_country_shp()
            sf = shapefile.Reader("C:/data/tools/sparc/input_data/countries/" + self.paese + ".shp")
            calc_poligono_controllo()

        with open(coords_check_file_in) as csvfile_in:
            lettore_comma = csv.reader(csvfile_in, delimiter=",", quotechar='"')
            next(lettore_comma)
            with open(coords_validated_file_out, 'wb') as csvfile_out:
                scrittore = csv.writer(csvfile_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                intestazioni = "id", "lat", "lon"
                scrittore.writerow(intestazioni)
                for row in lettore_comma:
                    if (punti_dentro_poligono_di_controllo(float(row[1]), float(row[2]))):
                        stringa = str(row[0]), str(row[1]), str(row[2])
                        scrittore.writerow(stringa)
                        dentro += 1
                    else:
                        fuori += 1
            csvfile_out.close()
        csvfile_in.close()
        print "dentro %d" % dentro, "fuori %d" % fuori

class CreateGeocodedShp(object):

    def __init__(self, paese):
        self.paese = paese
        self.outDriver = ogr.GetDriverByName("ESRI Shapefile")
        self.outShp = "C:/data/tools/sparc/input_data/geocoded/shp/" + self.paese + ".shp"

    def creazione_file_shp(self):
        # Remove output shapefile if it already exists
        if os.path.exists(self.outShp):
            self.outDriver.DeleteDataSource(self.outShp)

        #Set up blank lists for data
        x, y, nomeloc= [], [], []

        #read data from csv file and store in lists
        with open('C:/data/tools/sparc/input_data/geocoded/csv/'+ str(self.paese) + '.csv', 'rb') as csvfile:
            r = csv.reader(csvfile, delimiter=';')
            for i, row in enumerate(r):
                if i > 0: #skip header
                    divisa = row[0].split(",")
                    #print divisa[0]
                    nomeloc.append(divisa[0])
                    x.append(float(divisa[1]))
                    y.append(float(divisa[2]))
                    #date.append(''.join(row[1].split('-')))#formats the date correctly
                    #target.append(row[2])

        #Set up shapefile writer and create empty fields
        w = shapefile.Writer(shapefile.POINT)
        w.autoBalance = 1 #ensures gemoetry and attributes match
        w.field('ID','N')
        w.field('location','C', 50)
        # w.field('Date','D')
        # w.field('Target','C',50)
        # w.field('ID','N')

        #loop through the data and write the shapefile
        for j,k in enumerate(x):
            w.point(k,y[j]) #write the geometry
            w.record(k,nomeloc[j]) #write the attributes

        #Save shapefile
        w.save(self.outShp)