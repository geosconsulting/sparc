# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

import os,sys
from osgeo import gdal
from osgeo import gdalnumeric
from osgeo.gdalconst import *
import numpy as np
import glob

gdal.AllRegister()
use_numeric = False

def prepare_iso_list():

    direttorio = r'C:\data\tools\sparc\input_data\flood\gar15_ar\Flood'

    lista = []
    for direttorio_principale, direttorio_secondario, file_vuoto in os.walk(direttorio):
        if direttorio_principale != direttorio:
            lista.append(direttorio_principale)

    return lista

def convert_floods_grd_tif(dirPaese):

    os.chdir(dirPaese)
    iso_paese = dirPaese.split("\\")[-1]
    print iso_paese
    stringa_ricerca = "*.grd"
    lista_floods = glob.glob(stringa_ricerca)
    print lista_floods
    for raster in lista_floods:
        tr = raster.split("__")[1].split(".")[0]
        print("Processo " + tr)
        ds = gdal.Open(raster, GA_ReadOnly)
        driver = ds.GetDriver()
        if ds is None:
            print 'Could not open raster'
            sys.exit(1)

        #get image size
        rows = ds.RasterYSize
        cols = ds.RasterXSize

    # get the band and block sizes
        raster = ds.GetRasterBand(1)
        data = raster.ReadAsArray().astype(np.float)
        maschera = np.greater(data, 0)

        filename = dirPaese + "\\" + iso_paese + "_" + tr + ".tif"
        print filename
        outDataset = driver.Create(filename, cols, rows, 1, GDT_Int16)
        outBand = outDataset.GetRasterBand(1)
        outBand.WriteArray(maschera * int(tr), 0, 0)
        raster.FlushCache()
        raster.SetNoDataValue(-99)
        geoTransform = ds.GetGeoTransform()
        outDataset.SetGeoTransform(geoTransform)

def merge_floods(dirPaese):

    os.chdir(dirPaese)
    iso_paese = dirPaese.split("\\")[-1]
    print iso_paese
    stringa_ricerca = "*.tif"
    lista_floods_rcl = glob.glob(stringa_ricerca)
    print lista_floods_rcl
    for floodo in lista_floods_rcl:
        rp = floodo.split("_")[1].split(".")[0]
        if rp == '25':
            im_rp_25 = floodo
        elif rp == '50':
            im_rp_50 = floodo
        elif rp == '100':
            im_rp_100 = floodo
        elif rp == '200':
            im_rp_200 = floodo
        elif rp == '500':
            im_rp_500 = floodo
        elif rp == '1000':
            im_rp_1000 = floodo

    ar25 = gdalnumeric.LoadFile(im_rp_25).astype(np.int16)
    ar50 = gdalnumeric.LoadFile(im_rp_50).astype(np.int16)
    ar100 = gdalnumeric.LoadFile(im_rp_100).astype(np.int16)
    ar200 = gdalnumeric.LoadFile(im_rp_200).astype(np.int16)
    ar500 = gdalnumeric.LoadFile(im_rp_500).astype(np.int16)
    ar1000 = gdalnumeric.LoadFile(im_rp_1000).astype(np.int16)
    somma = ar25 + ar50 + ar100 + ar200 + ar500 + ar1000
    gdalnumeric.SaveArray(somma, dirPaese + "\\" + iso_paese + "_all_rp.tif", format="GTiff", prototype=im_rp_1000)

def reclass_flood(dir_paese):

    # Import arcpy module
    import arcpy

    # Check out any necessary licenses
    arcpy.CheckOutExtension("spatial")
    from arcpy import env
    env.overwriteOutput = "true"
    iso_paese = dir_paese.split("\\")[-1]

    # Local variables:
    paese_all_rp = dir_paese + "\\"  + iso_paese + "_all_rp.tif"
    paese_all_rp_rcl = dir_paese + "\\"  + iso_paese + "_all_rp_rcl.tif"

    # Process: Reclassify
    arcpy.gp.Reclassify_sa(paese_all_rp, "Value", "0 NODATA;1000 1000;1500 500;1700 200;1800 100;1850 50;1875 25", paese_all_rp_rcl, "DATA")

for dir_paese in prepare_iso_list():
     convert_floods_grd_tif(dir_paese)
     merge_floods(dir_paese)
     reclass_flood(dir_paese)

#dir_paese = r"C:\data\tools\sparc\input_data\flood\gar15_ar\Flood\RUS"
#convert_floods_grd_tif(dir_paese)
#merge_floods(dir_paese)
#reclass_flood(dir_paese)