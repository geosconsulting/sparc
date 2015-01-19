__author__ = 'fabio.lana'

import os, sys, glob
import numpy as np

from osgeo import ogr, gdal,osr
from osgeo import gdalnumeric
from osgeo.gdalconst import *
gdal.AllRegister()

#Arcpy module
import arcpy
arcpy.CheckOutExtension("spatial")
from arcpy import env
env.overwriteOutput = "true"

def selezioniamo_rasters(direttorio):

    lista_rasters_processo = []
    for direttorio_principale, direttorio_secondario,file_corrente in os.walk(direttorio):
        files_tif = glob.glob(direttorio_principale + "/*.tif")
        for file_tif in files_tif:
            fileName, fileExtension = os.path.splitext(file_tif)
            if 'rcl' in fileName:
                lista_rasters_processo.append(fileName + fileExtension)

    return lista_rasters_processo

def modifichiamo_rasters(lista_floods):

    for raster in lista_floods:
        tr = raster.split("_")[0]
        print("Processo " + tr)
        ds = gdal.Open(raster, GA_ReadOnly)
        driver = ds.GetDriver()
        if ds is None:
            print 'Could not open raster'
            sys.exit(1)
        else:
            rows = ds.RasterYSize
            cols = ds.RasterXSize
            try:
                banda_1 = ds.GetRasterBand(1)
            except RuntimeError, e:
                print 'No band %i found' % banda_1
                print e
                sys.exit(1)

        geotransform = ds.GetGeoTransform()
        originX = geotransform[0]
        originY = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]

        print originX, originY, pixelWidth, pixelHeight, rows, cols

        prj =  ds.GetProjection()
        outRasterSRS = osr.SpatialReference()
        prj_def = outRasterSRS.ImportFromWkt(ds.GetProjectionRef())
        print(prj_def)

        srs=osr.SpatialReference(wkt=prj)
        if srs.IsProjected:
            print srs.GetAttrValue('projcs')

        print srs.GetAttrValue('geogcs')
        print "[ PROJECTION ] = ",prj


        print "[ NO DATA VALUE ] = ", banda_1.GetNoDataValue()
        print "[ MIN ] = ", banda_1.GetMinimum()
        print "[ MAX ] = ", banda_1.GetMaximum()
        print "[ SCALE ] = ", banda_1.GetScale()

def conversione_gdalwarp(lista_floods):

    for file in lista_floods:
        file_ext = "C:/temp/" + str(str(file).split("\\")[1]).split("_")[0]+ ".tif"
        print file,file_ext
        #os.system('gdalwarp %s %s -t_srs "+proj=longlat +ellps=WGS84"' %(file,file_ext))

lista_rasters_invio = selezioniamo_rasters("C:/temp/merged")
#print lista_rasters_invio
#modifichiamo_rasters(lista_rasters_invio)
conversione_gdalwarp(lista_rasters_invio)