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
import arcpy
arcpy.CheckOutExtension("spatial")
from arcpy import env
env.overwriteOutput = "true"

#Custom Modules
import UtilitieSparc as us

class HazardAssessmentCountry(object):

    proj_dir = os.getcwd() + "/projects/"
    shape_countries = os.getcwd() + "/input_data/gaul/gaul_wfp.shp"

    def __init__(self,paese,admin,code):

        self.paese = paese
        self.admin = admin
        self.code = code
        self.dirOut = HazardAssessmentCountry.proj_dir + paese + "/" + admin + "/"

        scrittura_risultati = us.ManagePostgresDB(paese,admin)
        nome, iso2, iso3, wfp_area = scrittura_risultati.leggi_tabella()

        self.wfp_area = str(wfp_area).strip()
        self.iso3 = iso3

        self.population_raster = "C:/data/tools/sparc/input_data/population/" + self.wfp_area + "/" + self.iso3 + "-POP/" + self.iso3 + "10v4.tif" #popmap10.tif"
        #self.flood_aggregated = os.getcwd() + "/input_data/flood/rp_aggregat.tif"
        self.flood_aggregated = os.getcwd() + "/input_data/flood/merged/" + self.paese + "_all_rp_rcl.tif"
        self.historical_accidents = os.getcwd() + "/input_data/historical_data/floods.csv"
        self.flood_directory = "C:/data/tools/sparc/input_data/flood/m1/"
        self.flood_rp25 = self.flood_directory + paese + "_25_M1.grd"
        self.flood_rp50 = self.flood_directory + paese + "_50_M1.grd"
        self.flood_rp100 = self.flood_directory + paese + "_100_M1.grd"
        self.flood_rp200 = self.flood_directory + paese + "_200_M1.grd"
        self.flood_rp500 = self.flood_directory + paese + "_500_M1.grd"
        self.flood_rp1000 = self.flood_directory + paese + "_1000_M1.grd"

        self.flood_extents = []
        self.flood_extents.append(self.flood_rp25)
        self.flood_extents.append(self.flood_rp50)
        self.flood_extents.append(self.flood_rp100)
        self.flood_extents.append(self.flood_rp200)
        self.flood_extents.append(self.flood_rp500)
        self.flood_extents.append(self.flood_rp1000)

    def estrazione_poly_admin(self):

        #filter_field_name = "ADM2_NAME"
        filter_field_name = "ADM2_CODE"

        # Get the input Layer
        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        inDataSource = inDriver.Open(self.shape_countries, 0)
        inLayer = inDataSource.GetLayer()

        #print self.admin,self.code

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
        out_layer = outDataSource.CreateLayer(str(out_lyr_name), geom_type=ogr.wkbMultiPolygon)

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
                    inFeature.GetField(i))

            # Set geometry as centroid
            geom = inFeature.GetGeometryRef()
            outFeature.SetGeometry(geom.Clone())
            # Add new feature to output Layer
            out_layer.CreateFeature(outFeature)

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
            admin_rast = arcpy.PolygonToRaster_conversion(admin_vect, "ADM2_CODE", admin_rast, "CELL_CENTER", "NONE", 0.0008333)
        except Exception as e:
            print e.message

        return "Raster Created....\n"

    def taglio_raster_popolazione(self):

        #CUT and SAVE Population within the admin2 area
        lscan_out_rst = arcpy.Raster(self.population_raster) * arcpy.Raster(admin_rast)
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

        for rp in self.flood_extents:
            #CUT and SAVE Flooded areas within the admin2 area
            flood_divided_rst = arcpy.Raster(rp) * arcpy.Raster(admin_rast)
            flood_out_divided = self.dirOut + rp.split("/")[7].split("_")[1] + "_fld.tif"
            flood_divided_rst.save(flood_out_divided)

        return "Clipped all floods.......\n"

    def calcolo_statistiche_zone_indondazione(self):
        flood_out = arcpy.Raster(self.dirOut + self.admin + "_agg.tif")
        pop_out = arcpy.Raster(self.dirOut + self.admin + "_pop.tif")
        pop_stat_dbf = self.dirOut + self.admin.lower() + "_pop_stat.dbf"
        global tab_valori
        tab_valori = arcpy.gp.ZonalStatisticsAsTable_sa(flood_out, "Value", pop_out, pop_stat_dbf ,"DATA","ALL")
        global pop_freqs
        pop_freqs = arcpy.da.SearchCursor(tab_valori,["VALUE", "SUM"])
        return "People in flood prone areas....\n"

