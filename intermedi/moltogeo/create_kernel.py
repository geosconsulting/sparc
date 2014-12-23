
import arcpy
from arcpy import env
import os

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

countries_shp_location = 'C:/data/tools/sparc/input_data/countries'
events_location = 'C:/data/tools/sparc/input_data/geocoded/shp/'
risk_map_location = 'C:/data/tools/sparc/input_data/geocoded/risk_map/'

def add_prj(paese):

    # set workspace environment where the shapefiles are located
    #env.workspace = "C:/data/input_data/countries"
    #env.workspace = countries_shp_location
    env.workspace = events_location
    inData = paese + ".shp"
    print "Proietto " + inData
    try:
        coordinateSystem = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
        arcpy.DefineProjection_management(inData, coordinateSystem)
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
        arcpy.AddError(arcpy.GetMessages(2))
    except Exception as e:
        print e.args[0]
        arcpy.AddError(e.args[0])

def create_heat_map(paese):

    # Local variables:
    event_file_shp = events_location + paese + ".shp"
    krn_map_file = risk_map_location + paese + ".tif"

    try:
        # Process: Kernel Density
        arcpy.gp.KernelDensity_sa(event_file_shp, "NONE", krn_map_file, "0.02", "", "SQUARE_MAP_UNITS")
    except arcpy.ExecuteError:
        print "Errore" + paese
        print arcpy.GetMessages(2)
        arcpy.AddError(arcpy.GetMessages(2))
    except Exception as e:
        print "Exception " + paese
        print e.args[0]
        arcpy.AddError(e.args[0])

# for file in os.listdir(events_location):
#     if file.endswith(".shp"):
#         paese_attivo = file.split(".")[0]
#         #add_prj(paese_attivo)
#         create_heat_map(paese_attivo)

create_heat_map("Turkmenistan")


def create_global_heat_map():

    event_file_shp = "C:/data/tools/sparc/input_data/geocoded/shp/global_accidents.shp"
    krn_map_file = "C:/data/tools/sparc/input_data/geocoded/risk_map/global_accidents.tif"

    try:
        arcpy.gp.KernelDensity_sa(event_file_shp, "NONE", krn_map_file, "0.02", "", "SQUARE_MAP_UNITS")
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
        arcpy.AddError(arcpy.GetMessages(2))
    except Exception as e:
        print e.args[0]
        arcpy.AddError(e.args[0])

