# -*- coding: utf-8 -*

#Standard Modules
import collections
from osgeo import gdal, ogr
import matplotlib.pyplot as plt
import pylab
import numpy as np
import scipy.interpolate
import scipy.optimize
from scipy.interpolate import interp1d
import os
import glob
import csv
import math
import os
import arcpy
arcpy.CheckOutExtension("spatial")
from arcpy import env
env.overwriteOutput = "true"

#Custom Modules
import UtilitieSparc as us

class HazardAssessmentCountry(object):

    proj_dir = os.getcwd() + "/projects/"
    shape_countries = os.getcwd() + "/input_data/gaul/gaul_wfp.shp"

    def __init__(self, paese, admin, code):

        self.paese = paese
        self.admin = admin
        self.code = code
        self.dirOut = HazardAssessmentCountry.proj_dir + paese + "/" + admin + "/"

        scrittura_risultati = us.ManagePostgresDB(paese,admin)
        nome, iso2, iso3, wfp_area = scrittura_risultati.leggi_tabella()

        self.wfp_area = str(wfp_area).strip()
        self.iso3 = iso3

        self.population_raster = "C:/data/tools/sparc/input_data/population/" + self.wfp_area + "/" + self.iso3 + "-POP/" + self.iso3 + "10.tif" #popmap10.tif"
        self.flood_aggregated = "C:/data/tools/sparc/input_data/flood/merged/" + self.paese + "_all_rp_rcl.tif"
        self.historical_accidents = "C:/data/tools/sparc/input_data/historical_data/floods.csv"

    def estrazione_poly_admin(self):

        #filter_field_name = "ADM2_NAME"
        filter_field_name = "ADM2_CODE"

        # Get the input Layer
        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        inDataSource = inDriver.Open(self.shape_countries, 0)
        inLayer = inDataSource.GetLayer()
        inLayerProj = inLayer.GetSpatialRef()
        #print inLayerProj

        #inLayer.SetAttributeFilter("ADM2_NAME = '" + str(self.admin) + "'")
        print "ADM2_CODE=" + str(self.code)
        inLayer.SetAttributeFilter("ADM2_CODE=" + str(self.code))

        # Create the output LayerS
        outShapefile = os.path.join(self.dirOut + self.admin + ".shp")
        outDriver = ogr.GetDriverByName("ESRI Shapefile")

        # Remove output shapefile if it already exists
        if os.path.exists(outShapefile):
            outDriver.DeleteDataSource(outShapefile)

        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(outShapefile)
        out_lyr_name = os.path.splitext(os.path.split(outShapefile)[1])[0]
        out_layer = outDataSource.CreateLayer(str(out_lyr_name),inLayerProj, geom_type=ogr.wkbMultiPolygon)

        # Add input Layer Fields to the output Layer if it is the one we want
        inLayerDefn = inLayer.GetLayerDefn()
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            fieldName = fieldDefn.GetName()
            if fieldName not in filter_field_name:
                continue
            out_layer.CreateField(fieldDefn)

        # Get the output Layer's Feature Definition
        outLayerDefn = out_layer.GetLayerDefn()

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
                    1)
                    #inFeature.GetField(i))

            # Set geometry as centroid
            geom = inFeature.GetGeometryRef()
            outFeature.SetGeometry(geom.Clone())
            # Add new feature to output Layer
            out_layer.CreateFeature(outFeature)

        # Close DataSources
        inDataSource.Destroy()
        outDataSource.Destroy()
        return "Admin extraction......"

    def conversione_vettore_raster_admin(self):

        global admin_vect
        admin_vect = self.dirOut + self.admin + ".shp"

        global admin_rast
        if len(self.admin) > 5:
            admin = self.admin[0:3]
        admin_rast = self.dirOut + self.admin + "_rst.tif"

        try:
            admin_rast = arcpy.PolygonToRaster_conversion(admin_vect, "ADM2_CODE", admin_rast, "CELL_CENTER", "NONE", 0.0008333)
        except Exception as e:
            print e.message

        return "Raster Created...."

    def taglio_raster_popolazione(self):

        #CUT and SAVE Population within the admin2 area
        lscan_out_rst = arcpy.Raster(self.population_raster) * arcpy.Raster(admin_rast)
        lscan_out = self.dirOut + self.admin + "_pop.tif"
        lscan_out_rst.save(lscan_out)
        return "Population clipped...."

    def taglio_raster_inondazione_aggregato(self):

        #CUT and SAVE Flooded areas within the admin2 area
        flood_out_rst = arcpy.Raster(self.flood_aggregated) * arcpy.Raster(admin_rast)
        flood_out = self.dirOut + self.admin + "_agg.tif"
        flood_out_rst.save(flood_out)
        arcpy.CalculateStatistics_management(flood_out)
        try:
            proprieta = arcpy.GetRasterProperties_management(flood_out, "UNIQUEVALUECOUNT")
            print "%d Return Periods" % proprieta
            return "Flood"
        except:
            pass
            return "NoFlood"

    def calcolo_statistiche_zone_inondazione(self):
        flood_out = arcpy.Raster(self.dirOut + self.admin + "_agg.tif")
        pop_out = arcpy.Raster(self.dirOut + self.admin + "_pop.tif")
        pop_stat_dbf = self.dirOut + self.admin.lower() + "_pop_stat.dbf"
        tab_valori = arcpy.gp.ZonalStatisticsAsTable_sa(flood_out, "Value", pop_out, pop_stat_dbf , "DATA", "ALL")
        pop_freqs = arcpy.da.SearchCursor(tab_valori,["Value", "SUM"])
        return "People in flood prone areas....\n"

class MonthlyAssessmentCountry(object):

    monthly_precipitation_dir = "C:/data/tools/sparc/input_data/precipitation/"

    def __init__(self, paese, admin, code):

        self.paese = paese
        self.admin = admin
        self.code = code
        self.dirOut = HazardAssessmentCountry.proj_dir + paese + "/" + admin + "/"

        scrittura_risultati = us.ManagePostgresDB(paese,admin)
        nome, iso2, iso3, wfp_area = scrittura_risultati.leggi_tabella()

        self.wfp_area = str(wfp_area).strip()
        self.iso3 = iso3

        self.population_raster = "C:/data/tools/sparc/input_data/population/" + self.wfp_area + "/" + self.iso3 + "-POP/" + self.iso3 + "10.tif" #popmap10.tif"
        self.flood_aggregated = "C:/data/tools/sparc/input_data/flood/merged/" + self.paese + "_all_rp_rcl.tif"
        self.historical_accidents_file = "C:/data/tools/sparc/input_data/historical_data/floods - refine.csv"

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
        print admin_rast

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
        mese_di_massimo_valore = max(dizionario_in, key=dizionario_in.get)
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

        return "Monthly subdivision of incidents calculated....\n"

    def population_flood_prone_areas(self):

        global population_in_flood_prone_areas
        try:
            tabella_calcolata = self.dirOut + self.admin + "_pop_stat.dbf"
            tab_cur_pop = arcpy.da.SearchCursor(tabella_calcolata, "*")
            campo_tempo_ritorno = tab_cur_pop.fields.index('Value')
            campo_pop_affected = tab_cur_pop.fields.index('SUM')
            population_in_flood_prone_areas = {}
            for riga_pop in tab_cur_pop:
                tempo_ritorno = riga_pop[campo_tempo_ritorno]
                population_tempo_ritorno = riga_pop[campo_pop_affected]
                if population_tempo_ritorno > 0:
                    population_in_flood_prone_areas[tempo_ritorno] = population_tempo_ritorno
        except:
            pass

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
                    persone_pesi['500'][peso_chiave] = persone
                elif iteratore == 6:
                    persone_pesi['1000'][peso_chiave-1] = persone

        return "Monthly people divided.....\n"


