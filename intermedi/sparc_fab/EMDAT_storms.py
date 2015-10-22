__author__ = 'fabio.lana'
from urllib2 import Request, urlopen
import json
import pandas as pd
from sqlalchemy import create_engine,MetaData
import csv
import os
import re
import pycountry
import psycopg2
from geopy.geocoders import Nominatim
from geopy.geocoders import GeoNames
import shapefile
import matplotlib.pylab as plt
from shapely.geometry import Point, Polygon, asShape, box
from osgeo import ogr
ogr.UseExceptions()

class ScrapingEMDAT(object):

    def __init__(self,iso,hazard):
        self.stringa_richiesta = 'http://www.emdat.be/disaster_list/php/search.php?continent=&region=&iso='+iso+'&from=1900&to=2015&group=&type=' + hazard
        self.engine = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports')
        self.connection = self.engine.connect()
        self.schema_emdat = 'em_dat'
        self.metadata = MetaData(self.engine,schema=self.schema_emdat)
        self.table_name = "sparc_emdat_" + hazard + "_" + iso

    def scrape_EMDAT(self):

        richiesta = Request(self.stringa_richiesta)
        risposta = urlopen(richiesta)
        ritornati = json.loads(risposta.read(), encoding='LATIN-1')

        return ritornati

    def write_in_db(self, df_danni):

        try:
            df_danni.to_sql(self.table_name, self.engine,schema= "em_dat")
            self.connection.close()
        except Exception as tabella_esiste:
            print tabella_esiste.message

    def read_from_db(self):

        try:
            df_da_sql = pd.read_sql_table(self.table_name, self.engine, index_col='disaster_no',schema= "em_dat")
            self.connection.close()
            print "Leggendo da " + self.table_name
            return df_da_sql
        except Exception as tabella_non_esiste:
            print tabella_non_esiste.message

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

        geocoding_testo = open("c:/sparc/input_data/geocoded/new_geocoded_EMDAT/" + self.paese + hazard + ".txt", "wb+")
        geocoding_testo_fail = open("c:/sparc/input_data/geocoded/new_geocoded_EMDAT/" + self.paese + hazard + "_fail.txt", "wb+")

        geocoding_testo.write("id,lat,lon,em_dat\n")
        geocoding_testo_fail.write("id,lat,lon,em_dat\n")

        for luogo_incidente in luoghi_incidenti:
            try:
                if luogo_incidente is not None:
                    ("Geocoding " + luogo_incidente)
                    location_geocoded = self.geolocator.geocode(luogo_incidente, timeout=30)
                    if location_geocoded:
                        scrittura = luogo_incidente + "," + str(location_geocoded.longitude) + "," + str(location_geocoded.latitude) + "\n"
                        print scrittura
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
            inShapefile = "C:/sparc/input_data/gaul/gaul_wfp_iso.shp"
            inDriver = ogr.GetDriverByName("ESRI Shapefile")
            inDataSource = inDriver.Open(inShapefile, 0)
            inLayer = inDataSource.GetLayer()
            #print "ADM0_NAME = '" + self.paese + "'"
            inLayer.SetAttributeFilter("ADM0_NAME = '" + str(self.paese) + "'")
            # Create the output LayerS
            outShapefile = "C:/sparc/input_data/countries/" + str(self.paese) + ".shp"
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
                #print fieldName
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

        coords_file_in = "c:/sparc/input_data/geocoded/new_geocoded_EMDAT/" + self.paese + self.hazard + ".txt"
        coords_file_out = str('c:/sparc/input_data/geocoded/new_geocoded_EMDAT/' + str(self.paese) + self.hazard + '.csv')

        dentro = 0
        fuori = 0

        if os.path.exists("C:/sparc/input_data/countries/" + self.paese + ".shp"):
            print "File controllo trovato in" + str("C:/sparc/input_data/countries/" + self.paese + ".shp")
            sf = shapefile.Reader("C:/sparc/input_data/countries/" + self.paese + ".shp")
        else:
            print "Devo estrarre"
            self.extract_country_shp()
            sf = shapefile.Reader("C:/sparc/input_data/countries/" + self.paese + ".shp")

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
        self.outShp = "C:/sparc/input_data/geocoded/new_geocoded_EMDAT/" + self.paese + self.hazard + ".shp"

    def creazione_file_shp(self):

        print("Lo scrivo in %s" % str(self.outShp))
        # Remove output shapefile if it already exists
        if os.path.exists(self.outShp):
            self.outDriver.DeleteDataSource(self.outShp)

        #Set up blank lists for data
        x, y, nomeloc= [], [], []

        #read data from csv file and store in lists
        with open('C:/sparc/input_data/geocoded/new_geocoded_EMDAT/'+ self.paese + self.hazard + '.csv', 'rb') as csvfile:
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
        if len(w._shapes)> 0:
            w.save(self.outShp)
        else:
            None

class ManagePostgresDBEMDAT(object):

    def all_country_db(self):

        schema = 'public'
        dbname = "geonode-imports"
        user = "geonode"
        password = "geonode"

        try:
            connection_string = "dbname=%s user=%s password=%s" % (dbname, user, password)
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

paese = pycountry.countries.get(name = 'Thailand')
iso = paese.alpha3
nome_paese = paese.name

#Fase WebScraping
scrapiamo = ScrapingEMDAT(iso,'Storm')
emdat_paese = scrapiamo.scrape_EMDAT()
df_emdat_paese = pd.DataFrame(emdat_paese['data'])
scrapiamo.write_in_db(df_emdat_paese)
df_valori_letti = scrapiamo.read_from_db()
df_valori_letti['inizio'] = pd.to_datetime(df_valori_letti['start_date'])
df_valori_letti['mese_inizio'] = pd.DatetimeIndex(df_valori_letti['inizio']).month
df_valori_letti['fine'] = pd.to_datetime(df_valori_letti['end_date'])
df_valori_letti['mese_fine'] = pd.DatetimeIndex(df_valori_letti['fine']).month
df_valori_letti['durata'] = abs(df_valori_letti['fine'] - df_valori_letti['inizio'])

data_minima = min(df_valori_letti['inizio'])
data_massima = max(df_valori_letti['inizio'])

df_valori_letti['total_affected'] = df_valori_letti['total_affected'].astype(int)
quanti_affected_per_mese = df_valori_letti.groupby('mese_inizio')['total_affected'].sum()
quanti_affected_per_mese.plot(kind='bar', title = 'People Affected by Month ' + str(paese.name) + " between " + str(data_minima.year) + " and " + str(data_massima.year), x= "Million")
plt.show()

quanti_per_mese = df_valori_letti.groupby('mese_inizio')['index'].count()
print quanti_per_mese

quanti_per_mese.plot(grid=True,kind='bar',title = 'Frequency of Events by Month ' + str(paese.name) + " between " + str(data_minima.year) + " and " + str(data_massima.year),table=False)
plt.show()

#FASE GEOCODING
geocodiamo = GeocodeEMDAT(nome_paese,'Storm')
locations_df = df_emdat_paese['location'].str.split(",")
locazioni_da_inviare_alla_geocodifica = []
for locazioni in locations_df:
    #print locations_df
    if locazioni is not None:
        for indice in range(0, len(locazioni)):
            locazione_singola = str(locazioni[indice]).strip()
            if ';' not in locazione_singola:
                locazioni_da_inviare_alla_geocodifica.append(locazione_singola)
            else:
                locazione_annidata = locazione_singola.split(";")
                for indice_annidato in range(0, len(locazione_annidata)):
                    locazioni_da_inviare_alla_geocodifica.append(str(locazione_annidata[indice_annidato]).strip())

#print locazioni_da_inviare_alla_geocodifica
geocodiamo.geolocate_accidents(locazioni_da_inviare_alla_geocodifica,'Storm')
geocodiamo.extract_country_shp()
geocodiamo.calc_poligono_controllo()


#FASE SHAPEFILE CREATION
shapiamo = CreateGeocodedShp(nome_paese,'Storm')
shapiamo.creazione_file_shp()


