import arcpy

def get_centroid(vect, dir_out, gdb, admin2):

    adm2_centroid = arcpy.FeatureToPoint_management(vect, dir_out + gdb + admin2 + "_cntrd", "CENTROID")
    coords = arcpy.da.SearchCursor(adm2_centroid,["SHAPE@XY"])
    for polyg in coords:
        x,y = polyg[0]
    return x, y

