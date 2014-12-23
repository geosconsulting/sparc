import os, arcpy, datetime, csv
from arcpy import env
from arcpy.sa import *
os.environ['ESRI_SOFTWARE_CLASS'] = 'Professional' 
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

workspace = r"C:\TEMP"

# raster_LandChange_eval = r"C:\temp\ForAndrea_LandCoverToolPart1\LCCTool_part120140915_093747\land_cover_change_evaluation_2001001to2011001.tif"
# raster_LandChange_negative = r"C:\temp\ForAndrea_LandCoverToolPart1\LCCTool_part120140915_093747\land_cover_change_2001001to2011001_negative.tif"
# admin_shapefile = r"C:\temp\ForAndrea_LandCoverToolPart1\LCCTool_part120140915_093747\zwe_bnd_adm2_250k_cso.shp"
# zone_field = "new_admin"
# workspace = r"C:\temp"

# raster_LandChange_eval = r"C:\temp\LCCTool_part120140911_143823\land_cover_change_evaluation_2001001to2010001.tif"
# raster_LandChange_negative = r"C:\temp\LCCTool_part120140911_143823\land_cover_change_2001001to2010001_negative.tif"
# admin_shapefile = r"C:\Data\LandCoverChange_tool\admin_test.shp"
# zone_field = "admin_code"
# workspace = r"C:\temp"
#
raster_LandChange_eval = arcpy.GetParameterAsText(0)
raster_LandChange_negative = arcpy.GetParameterAsText(1)
admin_shapefile = arcpy.GetParameterAsText(2)
zone_field = arcpy.GetParameterAsText(3)
workspace = arcpy.GetParameterAsText(4)

###create working folder

today = datetime.date.today()
hour = str(datetime.datetime.now())[11:13] + str(datetime.datetime.now())[14:16] + str(datetime.datetime.now())[17:19]
todaystr = today.isoformat()
todaystr = todaystr.replace("-", "")
todaystr = "LCCTool_part2_" + todaystr + "_" + hour

workspace = os.path.join(workspace,todaystr)
if not os.path.exists(workspace):
        os.mkdir(workspace)

env.workspace = workspace

print "Working folder created: " + workspace
arcpy.AddMessage("Working folder created: " + workspace)
new_admin_shapefile = os.path.basename(admin_shapefile)
arcpy.Copy_management(admin_shapefile, new_admin_shapefile)

admin_shapefile = new_admin_shapefile

### performing the zonal statistics
print "Performing the zonal statistics about LC change"
arcpy.AddMessage("Performing the zonal statistics about LC change")
outZSaT = ZonalStatisticsAsTable(admin_shapefile, zone_field, raster_LandChange_eval,"zonal_stat_LCchange.dbf", "DATA", "MEAN")
###make  join
arcpy.JoinField_management(admin_shapefile, zone_field, "zonal_stat_LCchange.dbf", zone_field, ["MEAN","COUNT"])

### performing the zonal statistics on negative change
print "Calculating the total negative change by admin"
arcpy.AddMessage("Calculating the total negative change by admin")
outZSaT = ZonalStatisticsAsTable(admin_shapefile, zone_field, raster_LandChange_negative,
                                 "zonal_stat_LCchange_negative.dbf", "DATA", "SUM")
###make  join
arcpy.JoinField_management(admin_shapefile, zone_field, "zonal_stat_LCchange_negative.dbf", zone_field, ["SUM"])

#calculating the percentage of negative change by admin
arcpy.AddField_management(admin_shapefile, "Neg_change", "FLOAT","", "", "", "", "NULLABLE")
#expression = "- (!SUM! / !COUNT! * 100)"
#arcpy.CalculateField_management(admin_shapefile, "Neg_change", expression), "PYTHON_9.3")

codeblock = """def test(sum, count):
    if sum < 0:
        var = - (sum / count * 100)
    else:
        var = 0
    return var"""

arcpy.CalculateField_management(admin_shapefile,"Neg_change","test( !SUM!, !COUNT!)","PYTHON_9.3",codeblock)

arcpy.AddMessage("Processing succeeded. Outputs raster: " + workspace + ". Admin compiled: " + admin_shapefile)
