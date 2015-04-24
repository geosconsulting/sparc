__author__ = 'fabio.lana'
from osgeo import ogr
ogr.UseExceptions()

def crea_VRTLayer():

    inDataSourceVRT = ogr.Open("C:/Users/fabio.lana/PycharmProjects/Python_zandbergen/gdal/cyclones.vrt", 1)

    return inDataSourceVRT


