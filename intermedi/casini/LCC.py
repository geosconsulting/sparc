import os, arcpy, datetime
from arcpy import env
from arcpy.sa import *
os.environ['ESRI_SOFTWARE_CLASS'] = 'Professional' 
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

#raster_LandChange_eval = r"C:\data\tools\sparc\input_data\land_degradation\Indonesia_LCC_2001_2012.tif"
#raster_LandChange_negative = r"C:\data\tools\sparc\input_data\land_degradation\Indonesia_LCC_2001_2012_negative.tif"
#admin_shapefile = r"C:\data\test_lc\indonesia\indonesia.shp"
zone_fields = ['ADM0_CODE','ADM1_CODE', 'ADM2_CODE']
#workspace = r"C:\temp"

raster_LandChange_eval = arcpy.GetParameterAsText(0)
raster_LandChange_negative = arcpy.GetParameterAsText(1)
admin_shapefile = arcpy.GetParameterAsText(2)
ot_dir = arcpy.GetParameterAsText(3)

###create working folder
today = datetime.date.today()
hour = str(datetime.datetime.now())[11:13] + str(datetime.datetime.now())[14:16] + str(datetime.datetime.now())[17:19]
todaystr = today.isoformat()
todaystr = todaystr.replace("-", "")
todaystr = "LCCTool_" + todaystr + "_" + hour

workspace = os.path.join(ot_dir, todaystr)
arcpy.AddMessage(workspace)
print workspace
if not os.path.exists(workspace):
    os.mkdir(workspace)
env.workspace = workspace

#print "Working folder created: " + workspace
arcpy.AddMessage("Working folder created: " + workspace)
new_admin_shapefile = os.path.basename(admin_shapefile)
arcpy.Copy_management(admin_shapefile, new_admin_shapefile)
admin_shapefile = new_admin_shapefile

indice = 1
for zone_field in zone_fields:
    print zone_field
    ### performing the zonal statistics
    #print "Performing the zonal statistics about LC change"
    arcpy.AddMessage("Performing the zonal statistics about LC change")
    nfile_change = "zstat_" + str(zone_field) +"_LCchange.dbf"
    arcpy.AddMessage(nfile_change)
    outZSaT = ZonalStatisticsAsTable(admin_shapefile, zone_field, raster_LandChange_eval,
                                     nfile_change, "DATA", "MEAN")

    ### performing the zonal statistics on negative change
    #print "Calculating the total negative change by admin"
    arcpy.AddMessage("Calculating the total negative change by admin")
    nfile_change_negative = "zstat_" + str(zone_field) +"_LCchange_negative.dbf"
    outZSaTNegativo = ZonalStatisticsAsTable(admin_shapefile, zone_field, raster_LandChange_negative,
                                     nfile_change_negative,"DATA", "SUM")

    #calculating the percentage of negative change by admin
    nome_campo = "nch" + str(indice)
    arcpy.AddField_management(nfile_change_negative, nome_campo , "FLOAT","", "", "", "", "NULLABLE")

    codeblock = """def test(sum, count):
            if sum < 0:
                var = - (sum / count * 100)
            else:
                var = 0
            return var"""

    arcpy.CalculateField_management(nfile_change_negative, nome_campo,"test( !SUM!, !COUNT!)","PYTHON_9.3", codeblock)

    if indice == 1:
        arcpy.JoinField_management(admin_shapefile, zone_field, nfile_change_negative, zone_field, ["nch1"])
    if indice == 2:
        arcpy.JoinField_management(admin_shapefile, zone_field, nfile_change_negative, zone_field, ["nch2"])
    if indice == 3:
        arcpy.JoinField_management(admin_shapefile, zone_field, nfile_change_negative, zone_field, ["nch3"])

    arcpy.AddMessage("Processing succeeded. Outputs raster: " + workspace + ". Admin compiled: " + admin_shapefile)

    indice += 1