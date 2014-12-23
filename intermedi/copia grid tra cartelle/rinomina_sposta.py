__author__ = 'fabio.lana'
import arcpy
from arcpy import env

direttorio_radice = "C:/data/tools/sparc/intermedi/casini/copia grid tra cartelle"
direttorio_da = "/iniziale"
direttorio_a = "/finale"

env.overwriteOutput = "true"
env.workspace = direttorio_radice + direttorio_da

rasters = arcpy.ListRasters("*", "GRID")
for raster in rasters:
    nome_out = direttorio_radice + direttorio_a + "/" + raster + "/" + raster + "12.tif"
    print(nome_out)
    arcpy.CopyRaster_management(raster, nome_out)
