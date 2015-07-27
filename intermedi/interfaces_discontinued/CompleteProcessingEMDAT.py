__author__ = 'fabio.lana'
from urllib2 import Request, urlopen
import json
import pandas as pd
from sqlalchemy import create_engine
import csv
import os
from geopy.geocoders import Nominatim
from geopy.geocoders import GeoNames
import shapefile
import psycopg2
import psycopg2.extras
from shapely.geometry import Point, Polygon, asShape, box
from osgeo import ogr
ogr.UseExceptions()

class ScrapingEMDAT(object):

    def __init__(self,area, iso_paese, hazard, paese):
        #self.continent = "Africa%27%2C%27Americas%27%2C%27Asia"
        self.paese = paese
        self.hazard = hazard
        self.stringa_richiesta = 'http://www.emdat.be/disaster_list/php/search.php?continent=&region=&iso=' + iso_paese + '&from=1900&to=2015&group=&type=' + self.hazard
        self.engine = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports')
        self.connection = self.engine.connect()
        self.table_name = "sparc_emdat_" + paese + "_" + hazard

    def scrape_EMDAT(self):

        richiesta = Request(self.stringa_richiesta)
        risposta = urlopen(richiesta)
        ritornati = json.loads(risposta.read(), encoding='LATIN-1')

        return ritornati

    def write_in_db(self,df_danni):

        df_danni.to_sql(self.table_name, self.engine, schema='em-dat')
        self.connection.close()

    def read_from_db(self, hazard):

        df_da_sql = pd.read_sql_table(self.table_name, self.engine, index_col='disaster_no',schema='em-dat')
        self.connection.close()
        return df_da_sql

class GeocodeEMDAT(object):

    def __init__(self, paese,hazard):
        self.paese = paese
        self.hazard = hazard
        self.geolocator = Nominatim()
        self.geolocator_geonames = GeoNames(country_bias = self.paese, username='fabiolana', timeout=1)

        self.totali = 0
        self.successo = 0
        self.insuccesso = 0

        self.poligono_controllo = []
        self.n = 0

    def geolocate_accidents(self, luoghi_incidenti, hazard):

        geocoding_testo = open("D:/JRC WFP/SPARC/sparc/input_data/geocoded/new_geocoded_EMDAT/" + self.paese + hazard + ".txt", "wb+")
        geocoding_testo_fail = open("D:/JRC WFP/SPARC/sparc/input_data/geocoded/new_geocoded_EMDAT/" + self.paese + hazard + "_fail.txt", "wb+")

        geocoding_testo.write("id,name,lat,lon\n")
        geocoding_testo_fail.write("id,name,lat,lon\n")

        for luogo_incidente in luoghi_incidenti:
            try:
                print("Geocoding " + luogo_incidente)
                location_geocoded = self.geolocator.geocode(luogo_incidente, timeout=30)
                if location_geocoded:
                    scrittura = luogo_incidente + "," + str(location_geocoded.longitude) + "," + str(location_geocoded.latitude) + "\n"
                    geocoding_testo.write(scrittura)
                    self.totali += 1
                    self.successo += 1
                else:
                    geocoding_testo_fail.write(luogo_incidente + "," + str(0) + "," + str(0) + "\n")
                    self.totali += 1
                    self.insuccesso += 1
            except ValueError as e:
                print e.message
        print "Total of %s events with %s successful %s unsuccessful and %d NULL" % (
        str(self.totali), str(self.successo), str(self.insuccesso), (self.totali - self.successo - self.insuccesso))

    def extract_country_shp(self):

            # Get the input Layer
            inShapefile = "D:/JRC WFP/SPARC/sparc/input_data/gaul/gaul_wfp_iso.shp"
            inDriver = ogr.GetDriverByName("ESRI Shapefile")
            inDataSource = inDriver.Open(inShapefile, 0)
            inLayer = inDataSource.GetLayer()
            print "ADM0_NAME = '" + self.paese + "'"
            inLayer.SetAttributeFilter("ADM0_NAME = '" + self.paese + "'")
            # Create the output LayerS
            outShapefile = "D:/JRC WFP/SPARC/sparc/input_data/countries/" + self.paese + ".shp"
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
                    outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(),inFeature.GetField(i))

                # Set geometry as centroid
                geom = inFeature.GetGeometryRef()
                outFeature.SetGeometry(geom.Clone())
                # Add new feature to output Layer
                outLayer.CreateFeature(outFeature)

            # Close DataSources
            inDataSource.Destroy()
            outDataSource.Destroy()

    def calc_poligono_controllo(self):

        coords_file_in = "D:/JRC WFP/SPARC/sparc/input_data/geocoded/new_geocoded_EMDAT/" + self.paese + self.hazard + ".txt"
        coords_file_out = str('D:/JRC WFP/SPARC/sparc/input_data/geocoded/new_geocoded_EMDAT/' + str(self.paese) + self.hazard + '.csv')

        dentro = 0
        fuori = 0

        if os.path.exists("D:/JRC WFP/SPARC/sparc/input_data/countries/" + self.paese + ".shp"):
            sf = shapefile.Reader("D:/JRC WFP/SPARC/sparc/input_data/countries/" + self.paese + ".shp")
        else:
            print "Devo estrarre"
            self.extract_country_shp()
            sf = shapefile.Reader("D:/JRC WFP/SPARC/sparc/input_data/countries/" + self.paese + ".shp")

        bbox = sf.bbox
        minx, miny, maxx, maxy = [x for x in bbox]

        bounding_box = box(minx, miny, maxx, maxy)
        with open(coords_file_in) as csvfile_in:
            lettore_comma = csv.reader(csvfile_in, delimiter=",", quotechar='"')
            next(lettore_comma)
            with open(coords_file_out, 'wb') as csvfile_out:
                scrittore = csv.writer(csvfile_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                intestazioni = "id", "lat", "lon"
                scrittore.writerow(intestazioni)
                for row in lettore_comma:
                    punto_corrente = Point(float(row[1]), float(row[2]))
                    print punto_corrente
                    if bounding_box.contains(punto_corrente):
                        stringa = str(row[0]), str(row[1]), str(row[2])
                        scrittore.writerow(stringa)
                        dentro += 1
                    else:
                        fuori += 1
            csvfile_out.close()
        csvfile_in.close()
        return dentro, fuori

class CreateGeocodedShp(object):

    def __init__(self, paese, hazard):
        self.paese = paese
        self.hazard = hazard
        self.outDriver = ogr.GetDriverByName("ESRI Shapefile")
        self.outShp = "D:/JRC WFP/SPARC/sparc/input_data/geocoded/new_geocoded_EMDAT/" + self.paese + self.hazard + ".shp"

    def creazione_file_shp(self):

        print("Lo scrivo in %s" % str(self.outShp))
        # Remove output shapefile if it already exists
        if os.path.exists(self.outShp):
            self.outDriver.DeleteDataSource(self.outShp)

        #Set up blank lists for data
        x, y, nomeloc= [], [], []

        #read data from csv file and store in lists
        with open('D:/JRC WFP/SPARC/sparc/input_data/geocoded/new_geocoded_EMDAT/'+ self.paese + self.hazard + '.csv', 'rb') as csvfile:
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

class ManagePostgresDBEMDAT(object):

    def __init__(self,user, password):

        self.schema = 'public'
        self.dbname = "geonode-imports"
        self.user = user
        self.password = password

    def all_country_db(self):

        try:
            connection_string = "dbname=%s user=%s password=%s" % (self.dbname, self.user,self.password)
            self.conn = psycopg2.connect(connection_string)
        except Exception as e:
            print e.message

        self.cur = self.conn.cursor()
        comando = "SELECT DISTINCT adm0_name FROM sparc_gaul_wfp_iso;"

        try:
            self.cur.execute(comando)
        except psycopg2.ProgrammingError as laTabellaNonEsiste:
            descrizione_errore = laTabellaNonEsiste.pgerror
            codice_errore = laTabellaNonEsiste.pgcode
            print descrizione_errore, codice_errore
            return codice_errore

        paesi = []
        for paese in self.cur:
            paesi.append(paese[0])

        return sorted(paesi)

    def select_ancillary_data_country(self, paese):

        try:
            connection_string = "dbname=%s user=%s password=%s" % (self.dbname, self.user, self.password)
            self.conn = psycopg2.connect(connection_string)
        except Exception as e:
            print e.message

        self.cur = self.conn.cursor()
        comando = "select * from sparc_wfp_countries as c,sparc_wfp_areas as a where c.name = '" + paese + "' and c.wfp_area=a.area_id;"

        try:
            self.cur.execute(comando)
        except psycopg2.ProgrammingError as errore:
            codice_errore = errore.pgcode
            print codice_errore
            return codice_errore

        for valore in self.cur:
            area = valore[7]

        return area
