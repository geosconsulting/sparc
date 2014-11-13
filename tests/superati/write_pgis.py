__author__ = 'fabio.lana'
from osgeo import ogr
from osgeo import osr

def connessione():
    ## PostgreSQL available?
    driverName = "PostgreSQL"
    drv = ogr.GetDriverByName(driverName)
    if drv is None:
        print "%s driver not available.\n" % driverName
    else:
        print "%s driver IS available.\n" % driverName

    database = 'sparc'
    usr = 'postgres'
    pw = 'sparc'

    connection_string = "PG:dbname='%s' user='%s' password='%s'" % (database, usr, pw)
    ogrds = ogr.Open(connection_string)
    return ogrds

def scrittura_pgis(ogrds, table, cicloni_csv,colonna_geom):

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    layer = ogrds.CreateLayer(table, srs, ogr.wkbUnknown, ['OVERWRITE=YES'])
    layerDefn = layer.GetLayerDefn()

    for riga in cicloni_csv:
        poligono_wkt = riga[colonna_geom]
        poligono = ogr.CreateGeometryFromWkt(poligono_wkt)
        feature = ogr.Feature(layerDefn)
        layer.StartTransaction()
        feature.SetGeometry(poligono)
        layer.CreateFeature(feature)

    layer.CommitTransaction()

