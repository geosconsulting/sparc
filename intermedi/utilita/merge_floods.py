# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

import os,sys
from osgeo import ogr, gdal
from osgeo import gdalnumeric
from osgeo.gdalconst import *
import numpy as np
import glob
gdal.AllRegister()

os.chdir(r'C:\data\tools\sparc\input_data\flood\m1')
use_numeric = False

def reclass_floods(paese):
    global lista_floods, raster, tr, ds, driver, rows, cols, data, maschera, filename, outDataset, outBand, geoTransform
    stringa_ricerca = "%s*.grd" % paese
    lista_floods = glob.glob(stringa_ricerca)
    print lista_floods
    for raster in lista_floods:
        tr = raster.split("_")[1]
        print("Processo " + tr)
        ds = gdal.Open(raster, GA_ReadOnly)
        driver = ds.GetDriver()
        if ds is None:
            print 'Could not open raster'
            sys.exit(1)

        # get image size
        rows = ds.RasterYSize
        cols = ds.RasterXSize

        # get the band and block sizes
        raster = ds.GetRasterBand(1)
        data = raster.ReadAsArray().astype(np.float)
        maschera = np.greater(data, 0)

        filename = "C:/data/tools/sparc/input_data/flood/masks/" + paese + "_" + tr + ".tif"
        outDataset = driver.Create(filename, cols, rows, 1, GDT_Int16)
        outBand = outDataset.GetRasterBand(1)
        outBand.WriteArray(maschera * int(tr), 0, 0)
        raster.FlushCache()
        raster.SetNoDataValue(-99)

        geoTransform = ds.GetGeoTransform()
        outDataset.SetGeoTransform(geoTransform)

def merge_floods(paese):
    os.chdir("C:/data/tools/sparc/input_data/flood/masks/")
    stringa_ricerca = "%s*.tif" % paese
    lista_floods_rcl = glob.glob(stringa_ricerca)
    print lista_floods_rcl
    im_rp_25 = lista_floods_rcl[3]
    im_rp_50 = lista_floods_rcl[5]
    im_rp_100 = lista_floods_rcl[1]
    im_rp_200 = lista_floods_rcl[2]
    im_rp_500 = lista_floods_rcl[4]
    im_rp_1000 = lista_floods_rcl[0]
    ar25 = gdalnumeric.LoadFile(im_rp_25).astype(np.int16)
    ar50 = gdalnumeric.LoadFile(im_rp_50).astype(np.int16)
    ar100 = gdalnumeric.LoadFile(im_rp_100).astype(np.int16)
    ar200 = gdalnumeric.LoadFile(im_rp_200).astype(np.int16)
    ar500 = gdalnumeric.LoadFile(im_rp_500).astype(np.int16)
    ar1000 = gdalnumeric.LoadFile(im_rp_1000).astype(np.int16)
    somma = ar25 + ar50 + ar100 + ar200 + ar500 + ar1000
    gdalnumeric.SaveArray(somma, "C:/data/tools/sparc/input_data/flood/merged/" + paese + "_all_rp.tif", format="GTiff", prototype = im_rp_1000)

def reclass_flood(paese):

    # Import arcpy module
    import arcpy

    # Check out any necessary licenses
    arcpy.CheckOutExtension("spatial")
    from arcpy import env
    env.overwriteOutput = "true"

    # Local variables:
    paese_all_rp = "C:\\data\\tools\\sparc\\input_data\\flood\\merged\\" + paese + "_all_rp.tif"
    paese_all_rp_rcl = "C:\\data\\tools\\sparc\\input_data\\flood\\merged\\" + paese + "_all_rp_rcl.tif"

    # Process: Reclassify
    arcpy.gp.Reclassify_sa(paese_all_rp, "Value", "0 NODATA;1000 1000;1500 500;1700 200;1800 100;1850 50;1875 25", paese_all_rp_rcl, "DATA")

#reclass_floods('Mozambique')
#merge_floods('Mozambique')
#reclass_flood('Mozambique')

