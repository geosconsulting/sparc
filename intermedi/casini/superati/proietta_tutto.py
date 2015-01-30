__author__ = 'fabio.lana'

# Import modules
import arcpy
from arcpy import env
import os

# Set environment settings
env.workspace = "C:/data/tools/sparc/input_data/flood/merged"

# Use ListFeatureClasses to generate a list of shapefiles
rstList = arcpy.ListRasters()

# Set coordinate system only for those inputs which have a defined spatial reference
for infc in rstList:
    # Determine if the input has a defined coordinate system
    dsc = arcpy.Describe(infc)
    sr = dsc.spatialReference
    if sr.Name == "Unknown":
        print "Sconosciuto"
        # skip
        continue
    else:
        # Determine the new output feature class path and name
        outFeatureClass = os.path.join(outWorkspace, infc.strip(".shp") + "_wgs84.shp")
        # Set output coordinate system
        outCS = "C:/Users/fabio.lana/AppData/Roaming/ESRI/Desktop10.2/ArcMap/Coordinate Systems/GCS_WGS_1984.prj"
        # Set transform method
        transform_method = "ETRS_1989_To_WGS_1984"

        arcpy.Project_management(infc, outFeatureClass, outCS, transform_method)



