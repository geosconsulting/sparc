__author__ = 'fabio.lana'
import os
from osgeo import ogr

def creazione_file():
    # Save extent to a new Shapefile
    outShapefile = "cyclones.shp"
    outDriver = ogr.GetDriverByName("ESRI Shapefile")

    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)

    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer("cyclones", geom_type=ogr.wkbPolygon)
    return outDataSource,outLayer

def creazione_campi(outLayer):

    # Add the fields we're interested in
    field_objid = ogr.FieldDefn("objid", ogr.OFTString)
    field_objid.SetWidth(8)
    outLayer.CreateField(field_objid)

    field_eventid = ogr.FieldDefn("eventid", ogr.OFTInteger)
    outLayer.CreateField(field_eventid)

    field_episodeid = ogr.FieldDefn("episodeid", ogr.OFTInteger)
    outLayer.CreateField(field_episodeid)

    field_eventtype = ogr.FieldDefn("eventtype", ogr.OFTInteger)
    outLayer.CreateField(field_eventtype)

    field_polygondate = ogr.FieldDefn("poly_date", ogr.OFTString)
    field_objid.SetWidth(10)
    outLayer.CreateField(field_polygondate)

    field_polygontype = ogr.FieldDefn("poly_typ", ogr.OFTString)
    field_polygontype.SetWidth(12)
    outLayer.CreateField(field_polygontype)

    field_polygonlabel = ogr.FieldDefn("poly_lab", ogr.OFTString)
    field_polygonlabel.SetWidth(12)
    outLayer.CreateField(field_polygonlabel)


def scrittura_valori(layerVRT, outDataSource, outLayer):

    for riga in layerVRT:
        # create the feature
        feature = ogr.Feature(outLayer.GetLayerDefn())
        feature.SetField("objid",riga.GetField("OBJECTID"))
        feature.SetField("eventid",riga.GetField("eventid"))
        feature.SetField("episodeid",riga.GetField("episodeid"))
        feature.SetField("eventtype",riga.GetField("eventtype"))
        feature.SetField("poly_date",riga.GetField("polygondate"))
        feature.SetField("poly_typ",riga.GetField("polygontype"))
        feature.SetField("poly_lab",riga.GetField("polygonlabel"))
        poligonoVRT = riga.GetGeometryRef()
        poligono_wkt = poligonoVRT.ExportToWkt()
        #print poligono_wkt
        poligono = ogr.CreateGeometryFromWkt(poligono_wkt)

        # Set the feature geometry using the polygon
        feature.SetGeometry(poligono)
        # Create the feature in the layer (shapefile)
        outLayer.CreateFeature(feature)
        # Destroy the feature to free resources
        feature.Destroy()

    # Destroy the data source to free resources
    outDataSource.Destroy()