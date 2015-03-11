__author__ = 'fabio.lana'

import unicodedata
import re
import dbf
import csv
import os
import psycopg2
from psycopg2 import extras
from geopy.geocoders import Nominatim
from geopy.geocoders import GeoNames
import shapefile
from osgeo import ogr
ogr.UseExceptions()
import arcpy
from arcpy import env

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

class UtilitieSparc(object):

    proj_dir = os.getcwd() + "/projects/"
    driver = ogr.GetDriverByName("ESRI Shapefile")
    #DA MAIN
    shape_countries = "input_data/gaul/gaul_wfp_iso.shp"

    campo_nome_paese = "ADM0_NAME"
    campo_iso_paese = "ADM0_CODE"
    campo_nome_admin = "ADM2_NAME"
    campo_iso_admin = "ADM2_CODE"
    shapefile = driver.Open(shape_countries)
    layer = shapefile.GetLayer()

    nome_paese = ""
    cod_paese = ""

    def __init__(self, paese, admin):

        self.dati_per_plot = {}
        self.dati_per_prob = {}

        self.paese = paese
        self.admin = admin
        self.dirOut = UtilitieSparc.proj_dir + paese + "/" + admin + "/"

    def lista_admin0(self):

       numFeatures = self.layer.GetFeatureCount()
       lista_stati = []
       lista_iso = []
       for featureNum in range(numFeatures):
           feature = self.layer.GetFeature(featureNum)
           nome_paese = feature.GetField(self.campo_nome_paese)
           code_paese = feature.GetField(self.campo_iso_paese)
           lista_stati.append(nome_paese)
           lista_iso.append(code_paese)

       seen = set()
       seen_add = seen.add
       lista_pulita = [x for x in lista_stati if not (x in seen or seen_add(x))]
       lista_admin0 = sorted(lista_pulita)
       return tuple(lista_admin0)

    def lista_admin2(self, country):

        country_capitalized = country.capitalize()

        self.layer.SetAttributeFilter(self.campo_nome_paese + " = '" + country_capitalized + "'")

        listone={}
        lista_iso = []
        lista_clean = []
        lista_admin2 = []

        for feature in self.layer:
            cod_admin = feature.GetField(self.campo_iso_admin)
            nome_zozzo = feature.GetField(self.campo_nome_admin)

            unicode_zozzo = nome_zozzo.decode('utf-8')
            nome_per_combo = unicodedata.normalize('NFKD', unicode_zozzo)

            no_dash = re.sub('-', '_', nome_zozzo)
            no_space = re.sub(' ', '', no_dash)
            no_slash = re.sub('/', '_', no_space)
            no_apice = re.sub('\'', '', no_slash)
            no_bad_char = re.sub(r'-/\([^)]*\)', '', no_apice)
            unicode_pulito = no_bad_char.decode('utf-8')
            nome_pulito = unicodedata.normalize('NFKD', unicode_pulito).encode('ascii', 'ignore')

            lista_iso.append(cod_admin)
            lista_clean.append(nome_pulito)
            lista_admin2.append(nome_per_combo)

        for i in range(len(lista_iso)):
            listone[lista_iso[i]] = {'name_orig': lista_admin2[i],'name_clean':lista_clean[i]}

        return lista_admin2, listone

    def creazione_struttura(self, admin_global):

        # Check in data structures exists and in case not create the directory named
        # after the country and all the directories
        UtilitieSparc.proj_dir
        os.chdir(UtilitieSparc.proj_dir)
        country_low = str(self.paese).lower()
        if os.path.exists(country_low):
           os.chdir(UtilitieSparc.proj_dir + country_low)
           admin_low = str(self.admin).lower()
           if os.path.exists(admin_low):
               pass
           else:
              os.mkdir(admin_low)
        else:
            os.chdir(UtilitieSparc.proj_dir)
            os.mkdir(country_low)
            os.chdir(UtilitieSparc.proj_dir + country_low)
            admin_low = str(self.admin).lower()
            if os.path.exists(admin_low):
                pass
            else:
                os.mkdir(admin_low)

        return "Project created......\n"

    def create_template(self,dir_template):
        os.chdir(dir_template)
        tabella = dbf.Table('monthly_values', 'month C(10);mean N(5,1)')
        return tabella.filename

class GeocodingEmDat(object):

    def __init__(self,paese):
        self.paese = paese
        self.historical_table = "c:/data/tools/sparc/input_data/historical_data/floods - refine.csv"
        self.geolocator = Nominatim()
        self.geolocator_geonames = GeoNames(country_bias=self.paese, username='fabiolana', timeout=1)
        self.outDriver = ogr.GetDriverByName("ESRI Shapefile")
        self.countries_shp_location = os.getcwd() + '/input_data/countries'
        self.outShp = os.getcwd() + "/input_data/geocoded/shp/" + self.paese + ".shp"
        self.events_location = os.getcwd() + '/input_data/geocoded/shp/'
        self.risk_map_location = os.getcwd() + '/input_data/geocoded/risk_map/'

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

        geocoding_success_file = "C:/data/tools/sparc/input_data/geocoded/text/" + self.paese + ".txt"
        geocoding_fail_file = "C:/data/tools/sparc/input_data/geocoded/text/" + self.paese + "_fail.txt"

        # Control if accidents have been geocoded already
        if os.path.exists(geocoding_success_file):
            return "Geocoded already!!"
            pass
        else:
            geocoding_success = open(geocoding_success_file, "wb+")
            geocoding_fail = open(geocoding_fail_file, "wb+")
            geocoding_success.write("id,lat,lon\n")
            geocoding_fail.write("id,lat,lon\n")

            try:
                for incidente in accidents.iteritems():
                    for location_non_geocoded in incidente[1]['locations'].iteritems():
                        totali += 1
                        posto_attivo = location_non_geocoded[1]
                        if posto_attivo != 'NoData':
                            try:
                                print("Geocoding " + posto_attivo)
                                #location_geocoded = self.geolocator.geocode(posto_attivo, timeout=30)
                                location_geocoded = self.geolocator_geonames.geocode(posto_attivo,timeout=30)
                                if location_geocoded:
                                    scrittura = posto_attivo + "," + str(location_geocoded.longitude) + "," + str(location_geocoded.latitude) + "\n"
                                    geocoding_success.write(scrittura)
                                    successo += 1
                                else:
                                    geocoding_fail.write(posto_attivo + "," + str(0) + "," + str(0) + "\n")
                                    insuccesso += 1
                            except ValueError as e:
                                print e.message
                print "Total of %s events with %s successful %s unsuccessful and %d NULL" % (
                str(totali), str(successo), str(insuccesso), (totali - successo - insuccesso))
                perc = float(successo) / float(totali) * 100.0
                print "Percentage %.2f of success" % perc
            except:
                print "No response from geocoding server"
                pass

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
            inShapefile = "input_data/gaul/gaul_wfp.shp"
            inDriver = ogr.GetDriverByName("ESRI Shapefile")
            inDataSource = inDriver.Open(inShapefile, 0)
            inLayer = inDataSource.GetLayer()
            inLayer.SetAttributeFilter("ADM0_NAME = '" + self.paese + "'")
            # Create the output LayerS
            outShapefile = "input_data/countries/" + self.paese + ".shp"
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

        coords_check_file_in = "input_data/geocoded/text/" + self.paese + ".txt"
        coords_validated_file_out = str('input_data/geocoded/csv/' + str(self.paese) + '.csv')
        if os.path.exists("input_data/countries/" + self.paese + ".shp"):
            sf = shapefile.Reader("input_data/countries/" + str(self.paese).lower() + ".shp")
            calc_poligono_controllo()
        else:
            extract_country_shp()
            sf = shapefile.Reader("input_data/countries/" + str(self.paese).lower() + ".shp")
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
        #print "dentro %d" % dentro, "fuori %d" % fuori

    def creazione_file_shp(self):

        # Remove output shapefile if it already exists
        if os.path.exists(self.outShp):
            self.outDriver.DeleteDataSource(self.outShp)

        #Set up blank lists for data
        x, y, nomeloc=[], [], []

        #read data from csv file and store in lists
        with open('input_data/geocoded/csv/'+str(self.paese) + '.csv', 'rb') as csvfile:
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

    def plot_mappa(self):

        def GetExtent(gt,cols,rows):
            ext=[]
            xarr=[0, cols]
            yarr=[0, rows]

            for px in xarr:
                for py in yarr:
                    x=gt[0]+(px*gt[1])+(py*gt[2])
                    y=gt[3]+(px*gt[4])+(py*gt[5])
                    ext.append([x,y])
                    #print x,y
                yarr.reverse()
            return ext

        pathToRaster = "input_data/geocoded/risk_map/" + self.paese + ".tif"
        from mpl_toolkits.basemap import Basemap
        import matplotlib.pyplot as plt
        import numpy as np
        from osgeo import gdal

        raster = gdal.Open(pathToRaster, gdal.GA_ReadOnly)
        array = raster.GetRasterBand(1).ReadAsArray()
        msk_array = np.ma.masked_equal(array, value=65535)
        # print 'Raster Projection:\n', raster.GetProjection()
        geotransform = raster.GetGeoTransform()
        cols = raster.RasterXSize
        rows = raster.RasterYSize
        ext = GetExtent(geotransform, cols, rows)
        #print ext[1][0], ext[1][1]
        #print ext[3][0], ext[3][1]

        #map = Basemap(projection='merc',llcrnrlat=-80, urcrnrlat=80, llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c')
        map = Basemap(projection='merc', llcrnrlat=ext[1][1], urcrnrlat=ext[3][1], llcrnrlon=ext[1][0], urcrnrlon=ext[3][0],lat_ts=20, resolution='c')

        # Add some additional info to the map
        map.drawcoastlines(linewidth=1.3, color='white')
        #map.drawrivers(linewidth=.4, color='white')
        map.drawcountries(linewidth=.75, color='white')
        #datain = np.flipud(msk_array)
        datain = np.flipud(msk_array)
        map.imshow(datain)#,origin='lower',extent=[ext[1][0], ext[3][0],ext[1][1],ext[3][1]])

        plt.show()

    def add_prj(self):

        env.workspace = self.events_location
        inData = self.paese + ".shp"
        print "Proietto " + inData
        try:
            coordinateSystem = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
            arcpy.DefineProjection_management(inData, coordinateSystem)
        except arcpy.ExecuteError:
            print arcpy.GetMessages(2)
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            print e.args[0]
            arcpy.AddError(e.args[0])

    def create_heat_map(self):

        # Local variables:
        event_file_shp = self.events_location + self.paese + ".shp"
        krn_map_file = self.risk_map_location + self.paese + ".tif"

        try:
            # Process: Kernel Density
            arcpy.gp.KernelDensity_sa(event_file_shp, "NONE", krn_map_file, "0.02", "", "SQUARE_MAP_UNITS")
        except arcpy.ExecuteError:
            print "Errore" + self.paese
            print arcpy.GetMessages(2)
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            print "Exception " + self.paese
            print e.args[0]
            arcpy.AddError(e.args[0])

class ConnectionPostgresDB(object):

    def __init__(self,paese,admin):
       self.paese = paese
       self.admin = admin
       self.schema = 'public'
       self.dbname = 'geonode-imports'
       self.user = 'geonode'
       self.password = 'geonode'

    def leggi_valori_amministrativi(self):

        conn = None
        try:
            connection_string = "dbname=%s user=%s password=%s" % (self.dbname, self.user, self.password)
            conn = psycopg2.connect(connection_string)
        except Exception as e:
            print e.message

        cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
        comando = "SELECT c.name,c.iso2,c.iso3,a.area_name FROM SPARC_wfp_countries c INNER JOIN SPARC_wfp_areas a ON c.wfp_area = a.area_id WHERE c.name = '" + self.paese + "';"
        #print comando
        cursor.execute(comando)
        row_count = 0
        for row in cursor:
            row_count += 1
            return row[0], row[1], row[2], row[3]

