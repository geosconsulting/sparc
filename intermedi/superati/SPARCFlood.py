# -*- coding: utf-8 -*
__author__ = 'fabio.lana'

import unicodedata
import re
import dbf
import csv
import os
from geopy.geocoders import Nominatim
from geopy.geocoders import GeoNames
import shapefile
import psycopg2
import collections
from osgeo import gdal, ogr
ogr.UseExceptions()

import matplotlib.pyplot as plt
import pylab
import numpy as np
import scipy.interpolate
import scipy.optimize
from scipy import stats
from scipy.interpolate import interp1d
from pandas import DataFrame
import pandas as pd
import os
import arcpy
arcpy.CheckOutExtension("spatial")
from arcpy import env
env.overwriteOutput = "true"

import os
import glob
import csv
import numpy as np
import math
import matplotlib.pyplot as plt
import pylab

import arcpy
arcpy.CheckOutExtension("spatial")
from arcpy import env
env.overwriteOutput = "true"

import os
import glob
import csv
import numpy as np
import math
import matplotlib.pyplot as plt
import pylab

import arcpy
arcpy.CheckOutExtension("spatial")
from arcpy import env
env.overwriteOutput = "true"


class ProjectFlood(object):

    proj_dir = "c:/data/projects/"
    shape_countries = "c:/data/input_data/gaul_2014_2008_2/gaul_wfp.shp"
    pop_distr = "c:/data/input_data/population/popmap10.tif"
    driver = ogr.GetDriverByName("ESRI Shapefile")
    shapefile = driver.Open(shape_countries)
    layer = shapefile.GetLayer()
    historical_table = "c:/data/input_data/historical_data/floods - refine.csv"

    def __init__(self,paese,admin):
        self.paese = paese
        self.admin = admin
        self.dirOut = HazardAssessment.proj_dir + paese + "/" + admin + "/out/"

class UtilitieSparc(ProjectFlood):

    campo_nome_paese = "ADM0_NAME"
    campo_iso_paese = "ADM0_CODE"
    campo_nome_admin = "ADM2_NAME"
    campo_iso_admin = "ADM2_CODE"

    nome_paese = ""
    cod_paese = ""

    def __init__(self, area,schema,tabella_pesi,tabella_pop_stat,tabella_cicloni):
        self.dati_per_plot = {}
        self.dati_per_prob = {}
        self.geolocator = Nominatim()
        self.geolocator_geonames = GeoNames(country_bias=self.paese, username='fabiolana', timeout=1)
        self.outDriver = ogr.GetDriverByName("ESRI Shapefile")
        self.outShp = "classes/geocodifica/shp/" + self.paese + ".shp"
        self.area = area
        self.schema = schema
        self.tabella_pesi = tabella_pesi
        self.tabella_pop_stat = tabella_pop_stat
        self.tabella_cicloni = tabella_cicloni
        try:
            self.conn = psycopg2.connect("dbname=sparc user=postgres")
        except Exception as e:
            print e.message
        self.cur = self.conn.cursor()

    def lista_admin0(self):

       numFeatures = self.layer.GetFeatureCount()
       lista_stati = []
       for featureNum in range(numFeatures):
           feature = self.layer.GetFeature(featureNum)
           nome_paese = feature.GetField(self.campo_nome_paese)
           lista_stati.append(nome_paese)

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
              os.chdir(UtilitieSparc.proj_dir + country_low + "/" + admin_global + "/")
              os.mkdir("out")
        else:
            os.chdir(UtilitieSparc.proj_dir)
            os.mkdir(country_low)
            os.chdir(UtilitieSparc.proj_dir + country_low)
            admin_low = str(self.admin).lower()
            if os.path.exists(admin_low):
                pass
            else:
                os.mkdir(admin_low)
                os.chdir(UtilitieSparc.proj_dir + country_low + "/" + admin_global + "/")
                os.mkdir("out")

        return "Project created......\n"

    def create_template(self,dir_template):
        os.chdir(dir_template)
        tabella = dbf.Table('monthly_values', 'month C(10);mean N(5,1)')
        return tabella.filename

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

        geocoding_success_file = "classes/geocodifica/text/" + self.paese + ".txt"
        geocoding_fail_file = "classes/geocodifica/text/" + self.paese + "_fail.txt"

        # Control if accidents have been geocoded already
        if os.path.exists(geocoding_success_file):
            print "Geocoded already!!"
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
            inShapefile = "C:/data/input_data/gaul_2014_2008_2/gaul_wfp.shp"
            inDriver = ogr.GetDriverByName("ESRI Shapefile")
            inDataSource = inDriver.Open(inShapefile, 0)
            inLayer = inDataSource.GetLayer()
            inLayer.SetAttributeFilter("ADM0_NAME = '" + self.paese + "'")
            # Create the output LayerS
            outShapefile = "C:/data/input_data/countries/" + self.paese + ".shp"
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

        coords_check_file_in = "classes/geocodifica/text/" + self.paese + ".txt"
        coords_validated_file_out = str('classes/geocodifica/csv/' + str(self.paese) + '.csv')
        if os.path.exists("C:/data/input_data/countries/" + self.paese + ".shp"):
            sf = shapefile.Reader("C:/data/input_data/countries/" + str(self.paese).lower() + ".shp")
            calc_poligono_controllo()
        else:
            extract_country_shp()
            sf = shapefile.Reader("C:/data/input_data/countries/" + str(self.paese).lower() + ".shp")
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
        with open('classes/geocodifica/csv/'+str(self.paese) + '.csv', 'rb') as csvfile:
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

    def cancella_tabella(self):

        comando_delete_table = "DROP TABLE " + self.schema + "." + self.tabella_pesi + " CASCADE;"

        try:
            self.cur.execute(comando_delete_table)
            return "Table deleted"
        except psycopg2.Error as delErrore:
            errore_delete_tabella = delErrore.pgerror
            return errore_delete_tabella

    def crea_tabella(self):
        try:
            comando = "CREATE TABLE " + self.schema + "." + self.tabella_pesi + " (id serial PRIMARY KEY,month integer,weight double precision);"
            print comando
            self.cur.execute(comando)
            #comando = "CREATE TABLE " + self.schema + "." + self.tabella_pesi + " (id serial PRIMARY KEY,month integer,weight double precision);"
            #self.cur.execute(comando)
            return "Table created"
        except psycopg2.Error as createErrore:
            descrizione_errore = createErrore.pgerror
            codice_errore = createErrore.pgcode
            return descrizione_errore, codice_errore
        #pass

    def updata_tabella(self):
        pass
        # for chiave, valore in val_prec.items():
        #     inserimento = "INSERT INTO " + self.schema + "." + self.nome_tabella + " (month, weight) VALUES (" + str(chiave) + "," + str(valore) + ");"
        #     self.cur.execute(inserimento)

    def leggi_tabella(self):

        conn_locale = psycopg2.connect("dbname=sparc_old user=postgres")
        cur_locale = conn_locale.cursor()
        comando_leggi_table = "SELECT ogc_fid FROM " + self.schema + "." + self.tabella_cicloni + ";"
        try:
            cur_locale.execute(comando_leggi_table)
            records = cur_locale.fetchall()
            return records
        except psycopg2.Error as delErrore:
            errore_delete_tabella = delErrore.pgerror
            return errore_delete_tabella

    def salva_cambi(self):
        try:
            self.cur.close()
            self.conn.commit()
            self.conn.close()
            return "Changes saved"
        except:
            return "Problem in saving"

class HazardAssessment(ProjectFlood):

    flood_aggregated = "c:/data/input_data/flood/rp_aggregat.tif"

    flood_rp25 = "C:/data/input_data/flood/gar15/h25m.tif"
    flood_rp50 = "C:/data/input_data/flood/gar15/h50m.tif"
    flood_rp100 = "C:/data/input_data/flood/gar15/h100m.tif"
    flood_rp200 = "C:/data/input_data/flood/gar15/h200m.tif"
    flood_rp500 = "C:/data/input_data/flood/gar15/h500m.tif"
    flood_rp1000 = "C:/data/input_data/flood/gar15/h1000m.tif"

    flood_extents = []
    flood_extents.append(flood_rp25)
    flood_extents.append(flood_rp50)
    flood_extents.append(flood_rp100)
    flood_extents.append(flood_rp200)
    flood_extents.append(flood_rp500)
    flood_extents.append(flood_rp1000)


    def __init__(self):
        self.dati_per_plot = {}
        self.dati_per_prob = {}


    def estrazione_poly_admin(self):

        filter_field_name = "ADM2_NAME"

        # Get the input Layer
        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        inDataSource = inDriver.Open(self.shape_countries, 0)
        inLayer = inDataSource.GetLayer()

        inLayer.SetAttributeFilter("ADM2_NAME = '" + self.admin + "'")
        numFeatures = inLayer.GetFeatureCount()

        # Create the output LayerS
        outShapefile = os.path.join(self.dirOut + self.admin + ".shp")
        outDriver = ogr.GetDriverByName("ESRI Shapefile")

        # Remove output shapefile if it already exists
        if os.path.exists(outShapefile):
            outDriver.DeleteDataSource(outShapefile)

        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(outShapefile)
        out_lyr_name = os.path.splitext( os.path.split(outShapefile )[1] )[0]
        outLayer = outDataSource.CreateLayer( out_lyr_name, geom_type=ogr.wkbMultiPolygon )

        # Add input Layer Fields to the output Layer if it is the one we want
        inLayerDefn = inLayer.GetLayerDefn()
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            fieldName = fieldDefn.GetName()
            if fieldName not in filter_field_name:
                continue
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
                if fieldName not in filter_field_name:
                    continue

                outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(),
                    inFeature.GetField(i))

            # Set geometry as centroid
            geom = inFeature.GetGeometryRef()
            outFeature.SetGeometry(geom.Clone())
            # Add new feature to output Layer
            outLayer.CreateFeature(outFeature)

        # Close DataSources
        inDataSource.Destroy()
        outDataSource.Destroy()
        return "Admin extraction......\n"

    def conversione_vettore_raster_admin(self):

        global admin_vect
        admin_vect = self.dirOut + self.admin + ".shp"

        global admin_rast
        if len(self.admin) > 5:
            admin = self.admin[0:3]
        admin_rast = self.dirOut + self.admin + "_rst.tif"

        try:
            admin_rast = arcpy.PolygonToRaster_conversion(admin_vect, "ADM2_NAME", admin_rast, "CELL_CENTER", "NONE", 0.0008333)
        except Exception as e:
            print e.message

        return "Raster Created....\n"

    def taglio_raster_popolazione(self):

        #CUT and SAVE Population within the admin2 area
        lscan_out_rst = arcpy.Raster(self.pop_distr) * arcpy.Raster(admin_rast)
        lscan_out = self.dirOut + self.admin + "_pop.tif"
        lscan_out_rst.save(lscan_out)
        return "Population clipped....\n"

    def taglio_raster_inondazione_aggregato(self):

        #CUT and SAVE Flooded areas within the admin2 area
        flood_out_rst = arcpy.Raster(self.flood_aggregated) * arcpy.Raster(admin_rast)
        flood_out = self.dirOut + self.admin + "_agg.tif"
        flood_out_rst.save(flood_out)
        return "Flood hazard aggregated clipped....\n"

    def taglio_raster_inondazione(self):

        indice = 0
        for rp in self.flood_extents:
            #tempo_ritorno = (rp.split("/")[5].split(".")[0].replace('h','').replace('m',''))
            #print("Calculating Return Period " + tempo_ritorno + " years")

            #CUT and SAVE Flooded areas within the admin2 area
            flood_divided_rst = arcpy.Raster(self.flood_extents[indice]) * arcpy.Raster(admin_rast)
            flood_out_divided = self.dirOut + rp.split("/")[5].split(".")[0] + "_fld.tif"
            flood_divided_rst.save(flood_out_divided)
            indice =+ indice

        return "Clipped all floods.......\n"

    def calcolo_statistiche_zone_indondazione(self):
        flood_out = arcpy.Raster(self.dirOut + self.admin + "_agg.tif")
        lscan_out = arcpy.Raster(self.dirOut + self.admin + "_pop.tif")
        global tab_valori
        tab_valori = arcpy.sa.ZonalStatisticsAsTable(flood_out, "VALUE", lscan_out, self.dirOut + self.admin.lower() + "_pop_stat", "NODATA")
        global pop_freqs
        pop_freqs = arcpy.da.SearchCursor(tab_valori, ["VALUE", "SUM"])
        return "People in flood prone areas....\n"

    def plot_affected(self):

        titolofinestra = "People Living in Flood Prone Areas"

        # Plotting affected people
        affected_people = {}
        for row in pop_freqs:
            affected_people[row[0]] = row[1]

        global affected_people_ordered
        affected_people_ordered = collections.OrderedDict(sorted(dict(affected_people).items()))

        fig = pylab.gcf()
        fig.canvas.set_window_title(titolofinestra)

        plt.grid(True)
        plt.title(self.admin)
        plt.xlabel("Return Periods")
        plt.ylabel("People in Flood Prone Area EM-DAT")
        plt.bar(range(len(affected_people_ordered)), affected_people_ordered.values(), align='center')
        plt.xticks(range(len(affected_people_ordered)), affected_people_ordered.keys(), rotation='vertical')
        plt.show()

    def plot_risk_curve(self):

        pop_temp = 0
        for periodo in affected_people_ordered.iteritems():
            annual_perc = 1/(periodo[0]/100.0)
            pop_temp = pop_temp + periodo[1]
            self.dati_per_plot[annual_perc] = pop_temp
            self.dati_per_prob[periodo[0]] = pop_temp

        fig = pylab.gcf()
        fig.canvas.set_window_title("Risk Curve")
        plt.grid(True)
        plt.title("Risk Curve using 6 Return Periods")
        plt.xlabel("Affected People", color="red")
        plt.ylabel("Annual Probabilities %", color="red")
        plt.tick_params(axis="x", labelcolor="b")
        plt.tick_params(axis="y", labelcolor="b")
        #plt.plot(sorted(pop_affected.keys(), reverse=True), sorted(pop_affected.values()), 'ro--')
        plt.plot(sorted(self.dati_per_plot.values(), reverse=True), sorted(self.dati_per_plot.keys()), 'ro--')
        for x, y in self.dati_per_plot.iteritems():
            plt.annotate(str(int(round(y, 2))), xy=(y,x), xytext=(5,5), textcoords='offset points', color='red', size=8)
        plt.show()

    def plot_risk_interpolation(self):

        x, y =  self.dati_per_plot.keys(),  self.dati_per_plot.values()
        # use finer and regular mesh for plot
        xfine = np.linspace(0.1, 4, 25)

        # interpolate with piecewise constant function (p =0)
        y0 = scipy.interpolate.interp1d(x, y, kind='nearest')
        # interpolate with piecewise linear func (p =1)
        y1 = scipy.interpolate.interp1d(x, y, kind='linear')
        plt.grid(True)
        pylab.plot(x, y, 'o', label='Affected People')
        pylab.plot(xfine, y0(xfine), label='nearest')
        pylab.plot(xfine, y1(xfine), label='linear')

        pylab.legend()
        pylab.xlabel('x')
        #pylab.savefig('interpolate.pdf')
        pylab.show()

    def interpolazione_tempi_ritorno_intermedi(self):

        dict_data = dict(self.dati_per_prob)
        dict_data_new = dict_data.copy()

        xdata = dict_data.keys()
        ydata = dict_data.values()

        f = interp1d(xdata, ydata)

        nuovi_RP = [75, 150, 250, 750]
        for xnew in nuovi_RP:
            popolazione_interpolata = f(xnew)
            dict_data_new[xnew] = float(popolazione_interpolata)
        ordinato_old = collections.OrderedDict(sorted(dict(dict_data).items()))
        global ordinato_new
        ordinato_new = collections.OrderedDict(sorted(dict(dict_data_new).items()))

    def gira_dati(self):
        global data_prob
        data_prob = {}
        for giratore in ordinato_new.iterkeys():
            data_prob[(1.0/giratore)*100] = ordinato_new[giratore]

    def plot_risk_interpolation_linear(self):

        titolo_plot = "Risk Curve using RP 25,50,75,100,150,200,500,750 and 1000 Years"
        x, y = data_prob.keys(), data_prob.values()

        xfine = np.linspace(0.1, 4, 25)

        y1 = scipy.interpolate.interp1d(x, y, kind='linear')
        plt.grid(True)

        fig = pylab.gcf()
        fig.canvas.set_window_title(titolo_plot)
        plt.grid(True)
        plt.title(self.admin)

        pylab.plot(x, y, 'o', label='Affected People')
        pylab.plot(xfine, y1(xfine), label='linear')

        for x, y in data_prob.iteritems():
            plt.annotate(str(int(round(y, 2))), xy=(y,x), xytext=(5,5), textcoords='offset points', color='red', size=8)

        pylab.legend()
        pylab.xlabel('x')
        #pylab.savefig('interpolate.pdf')
        pylab.show()

class MonthlyDistribution(ProjectFlood):

    monthly_precipitation_dir = "C:/data/input_data/precipitation/prec_monthly/"

    def build_value_list(self,list_val):

        la_lista_finale = {}
        for key, val in list_val.iteritems():
            if key == 'prc01.tif':
                la_lista_finale[1] = val
            elif key == 'prc02.tif':
                la_lista_finale[2] = val
            elif key == 'prc03.tif':
                la_lista_finale[3] = val
            elif key == 'prc04.tif':
                la_lista_finale[4] = val
            elif key == 'prc05.tif':
                la_lista_finale[5] = val
            elif key == 'prc06.tif':
                la_lista_finale[6] = val
            elif key == 'prc07.tif':
                la_lista_finale[7] = val
            elif key == 'prc08.tif':
                la_lista_finale[8] = val
            elif key == 'prc09.tif':
                la_lista_finale[9] = val
            elif key == 'prc10.tif':
                la_lista_finale[10] = val
            elif key == 'prc11.tif':
                la_lista_finale[11] = val
            elif key == 'prc12.tif':
                la_lista_finale[12] = val

        for k, v in la_lista_finale.iteritems():
            if v is None:
                la_lista_finale[k] = 0

        return la_lista_finale

    def cut_monthly_rasters(self):

        os.chdir(self.monthly_precipitation_dir)
        lista_raster = glob.glob("*.tif")
        admin_rast = self.dirOut + self.admin + "_rst.tif"

        valori_mensili = {}
        for raster_mese in lista_raster:
            mese_raster = arcpy.Raster(self.monthly_precipitation_dir + raster_mese)
            mese_tagliato = arcpy.sa.ExtractByRectangle(mese_raster, admin_rast)
            nome = self.dirOut + self.admin + "_" + str(raster_mese)
            mese_tagliato.save(nome)
            valori_mensili[raster_mese] = mese_tagliato.mean

        global dizionario_in
        dizionario_in = self.build_value_list(valori_mensili)
        with open(self.dirOut + self.admin + "_prec.csv", 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for linea in dizionario_in.iteritems():
                csvwriter.writerow(linea)

        global ritornati_somma
        ritornati_somma = sum(dizionario_in.values())

        return "Monthly Probability Function calculated....\n"

    def analisi_valori_da_normalizzare(self):

        mese_di_minimo_valore = min(dizionario_in, key = dizionario_in.get)
        minimo_valore = dizionario_in[mese_di_minimo_valore]
        mese_di_massimo_valore = max(dizionario_in, key = dizionario_in.get)
        massimo_valore = dizionario_in[mese_di_massimo_valore]

        #NORMALIZZAZIONE FATTA A MANO CALCOLANDO TUTTO
        #LO USO PERCHE ALTRIMENTI SI INCASINA LA GENERAZIONE DEI PLOTS
        global normalizzati
        normalizzati = {}
        for linea in dizionario_in.iteritems():
            x_new = (linea[1] - minimo_valore)/(massimo_valore-minimo_valore)
            normalizzati[linea[0]] = x_new

        with open(self.dirOut + self.admin + "_prec_norm.csv", 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for linea in normalizzati.iteritems():
                  csvwriter.writerow(linea)

        return "Monthly Probability Values normalized....\n"

    def historical_analysis_damages(self):

        import collections

        file_incidenti_in = open(self.historical_accidents_file)
        next(file_incidenti_in)
        mesi = []
        for linea in file_incidenti_in:
            splittato_comma = linea.split(",")
            if splittato_comma[2] == self.paese:
                if splittato_comma[0] == 0 or splittato_comma[1] == 0:
                    print splittato_comma[9]
                splittato_mese_inzio = splittato_comma[0].split("/")
                splittato_mese_fine = splittato_comma[1].split("/")
                #print splittato_mese_inzio[1], splittato_mese_fine[1]
                if splittato_mese_inzio[1]!=0 or splittato_mese_fine[0]!=0:
                    differenza = int(splittato_mese_fine[1]) - int(splittato_mese_inzio[1])
                    if differenza == 0:
                         mesi.append(int(splittato_mese_inzio[1]))
                    else:
                        mesi.append(int(splittato_mese_inzio[1]))
                        for illo in range(1, differenza+1):
                            mesi.append(int(splittato_mese_inzio[1]) + illo)
        file_incidenti_in.close()

        conta_mesi = collections.Counter(mesi)
        conta_mesi_ord = collections.OrderedDict(sorted(conta_mesi.items()))

        missing = []
        for indice in range(1, 13):
            if indice not in conta_mesi_ord:
                missing.append(indice)

        for valore in missing:
            conta_mesi_ord[valore] = 0

        global danni_mesi
        danni_mesi = collections.OrderedDict(sorted(conta_mesi_ord.items()))

        print danni_mesi

        return "Monthly subdivision of incidents calculated....\n"

    def plot_monthly_danni(self):

        labella_y = "Precipitation"
        titolo = "EM-DAT Registered Incidents"

        fig = pylab.gcf()
        fig.canvas.set_window_title(titolo)
        plt.grid(True)

        # Plot y1 vs x in blue on the left vertical axis.
        plt.xlabel("Months")
        plt.ylabel("Historical Incidents related with Floods EM-DAT", color="b")
        plt.tick_params(axis="y", labelcolor="b")
        plt.bar(range(len(danni_mesi)), danni_mesi.values(), align='center', color='g')

        plt.twinx()
        plt.ylabel(labella_y, color="r")
        plt.tick_params(axis="y", labelcolor="r")
        plt.plot(range(len(dizionario_in)), dizionario_in.values(), 'r--')
        plt.xticks(range(len(dizionario_in)), dizionario_in.keys())

        plt.title(self.admin)
        plt.show()

    def population_flood_prone_areas(self):

        global population_in_flood_prone_areas
        tabella_calcolata = self.dirOut + self.admin + "_pop_stat"
        tab_cur_pop = arcpy.da.SearchCursor(tabella_calcolata, "*")
        campo_tempo_ritorno = tab_cur_pop.fields.index('VALUE')
        campo_pop_affected = tab_cur_pop.fields.index('SUM')
        population_in_flood_prone_areas = {}
        for riga_pop in tab_cur_pop:
            tempo_ritorno = riga_pop[campo_tempo_ritorno]
            population_tempo_ritorno = riga_pop[campo_pop_affected]
            if population_tempo_ritorno > 0:
                population_in_flood_prone_areas[tempo_ritorno] = population_tempo_ritorno

        return "Population in flood prone areas calculated....\n"

    def calcolo_finale(self):

        global persone_pesi
        persone_pesi = dict()
        persone_pesi['25'] = {}
        persone_pesi['50'] = {}
        persone_pesi['100'] = {}
        persone_pesi['200'] = {}
        persone_pesi['500'] = {}
        persone_pesi['1000'] = {}

        iteratore = 0
        for persone_chiave, persone_valore in sorted(population_in_flood_prone_areas.iteritems()):
            iteratore += 1
            for peso_chiave, peso_valore in normalizzati.iteritems():
                persone = persone_valore * peso_valore
                if iteratore == 1:
                    persone_pesi['25'][peso_chiave] = persone
                elif iteratore == 2:
                    persone_pesi['50'][peso_chiave] = persone
                elif iteratore == 3:
                    persone_pesi['100'][peso_chiave] = persone
                elif iteratore == 4:
                    persone_pesi['200'][peso_chiave] = persone
                elif iteratore == 5:
                    #persone_pesi['500'][peso_chiave] = format(persone, '.0f')
                    for indice in range(1, 13):
                        persone_pesi['500'][indice] = 0
                    iteratore = 6
                elif iteratore == 6:
                    persone_pesi['1000'][peso_chiave-1] = persone
                    persone_pesi['1000'][peso_chiave] = 0.0

        return "Monthly people divided.....\n"

    def plottalo_bello(self):

        columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        rows = ['%d RP' % x for x in (1000, 500, 200, 100, 50, 25)]

        people_affected_rp = []
        for cada in persone_pesi.itervalues():
            myRoundedList = [round(elem, 2) for elem in cada.values()]
            people_affected_rp.append(myRoundedList)

        matrice = np.asarray(people_affected_rp)
        maximo_y = math.ceil(max(matrice.sum(0))/500)*500
        values = np.arange(0, maximo_y, 100000)
        value_increment = 1

        # Get some pastel shades for the colors
        colors = plt.cm.OrRd(np.linspace(0, 0.5, len(rows)))
        n_rows = len(persone_pesi)

        #index = np.arange(len(columns)) + 0.3
        index = np.arange(len(columns))
        bar_width = 1

        # Initialize the vertical-offset for the stacked bar chart.
        y_offset = np.array([0.0] * len(columns))

        # Plot bars and create text labels for the table
        cell_text = []
        for row in range(n_rows):
            plt.bar(index, people_affected_rp[row], bar_width, bottom=y_offset, color=colors[row])
            y_offset = y_offset + people_affected_rp[row]
            cell_text.append(['%d' % (x) for x in y_offset])
        # Reverse colors and text labels to display the last value at the top.
        colors = colors[::-1]
        cell_text.reverse()

        # Add a table at the bottom of the axes
        the_table = plt.table(cellText=cell_text,
                              rowLabels=rows,
                              rowColours=colors,
                              colLabels=columns,
                              loc ='bottom')

        # Adjust layout to make room for the table:
        plt.subplots_adjust(left=0.2, bottom=0.2)

        plt.ylabel("People at risk per Return Period")
        plt.yticks(values * value_increment), ['%d' % val for val in values]
        plt.xticks([])
        plt.title('People at risk by Return Period in ' + self.admin)
        plt.show()
