# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

from os import path
from os import listdir
from os.path import isfile, join
from dbfpy import dbf
import pandas as pd

import arcpy
import arcpy.da
from arcpy import env

arcpy.CheckOutExtension("spatial")
env.workspace = r"C:\data\tools\sparc\input_data\countries\countries.gdb"
popu = arcpy.Raster(r"C:\data\tools\sparc\input_data\population\Landscan\LandScan2013\ArcGIS\conversion\lscan13.tif")
tab_loc = r"C:\data\tools\sparc\input_data\population\calc_lscan/"
countries_dir = "C:\\data\\tools\\sparc\\input_data\\countries"
paesi = arcpy.ListFeatureClasses()

def conversione_campo_adm2_code_to_string_for_join():
    for i in range (0,len(paesi)):
        paese = paesi[i]
        arcpy.AddField_management(paese,"adm2_str","TEXT","10")
        cursore = arcpy.da.UpdateCursor(paese,("adm2_code", "adm2_str"))
        for rec in cursore:
            rec[1] = rec[0]
            cursore.updateRow(rec)

def calcolo_zonal_statistics():

    for i in range (0,len(paesi)):
        paese = paesi[i]
        tabula = tab_loc + paese.split("_")[1] + ".dbf"
        arcpy.sa.ZonalStatisticsAsTable(paese, "adm2_str", popu, tabula)

def join_dati_e_salvataggio_shps():

    onlyfiles = [f for f in listdir(tab_loc) if isfile(join(tab_loc,f))]

    env.workspace = r"C:\data\tools\sparc\input_data\countries\countries.gdb"
    for fileggio in sorted(onlyfiles):
        fileName, fileExtension = path.splitext(fileggio)
        if fileExtension == '.dbf':
            for paese in sorted(paesi):
                paese_gdb = paese.split("_")[1]
                if fileName == paese_gdb:
                    loca_dbf =  tab_loc + fileggio
                    loca_gdb = env.workspace + "/" + paese
                    print loca_dbf
                    print loca_gdb
                    linkata = arcpy.JoinField_management(loca_gdb,"adm2_str",loca_dbf,"adm2_str")
                    arcpy.FeatureClassToShapefile_conversion(loca_gdb, countries_dir)

def estrazione_dati_da_dbf_dello_shape_e_conversione_pandas():

    only_dbf_da_shp = [f for f in listdir(countries_dir) if isfile(join(countries_dir,f))]
    df_pop = pd.DataFrame(columns=['iso3','adm0_code','adm0_name','adm1_code','adm1_name','adm2_code','adm2_name','hectares','area_sqkm','area_sqft','pop'])

    contatore = 0
    for fileggio in sorted(only_dbf_da_shp):
        fileName, fileExtension = path.splitext(fileggio)
        if fileExtension == '.dbf':
            db = dbf.Dbf(countries_dir + "\\" + fileggio)
            for rec in db:
                df_pop.at[contatore,'iso3'] = rec["ISO3"]
                df_pop.at[contatore,'adm0_code'] = rec["ADM0_CODE"]
                df_pop.at[contatore,'adm0_name'] = rec["ADM0_NAME"]
                df_pop.at[contatore,'adm1_code'] = rec["ADM1_CODE"]
                df_pop.at[contatore,'adm1_name'] = rec["ADM1_NAME"]
                df_pop.at[contatore,'adm2_code'] = rec["ADM2_CODE"]
                df_pop.at[contatore,'adm2_name'] = rec["ADM2_NAME"]
                df_pop.at[contatore,'hectares'] = rec["HECTARES"]
                df_pop.at[contatore,'area_sqkm'] = rec["AREA_SQKM"]
                df_pop.at[contatore,'area_sqft'] = rec["AREA_SQFT"]
                df_pop.at[contatore,'pop'] = rec["SUM"]
                contatore += 1

    return df_pop

from sqlalchemy import create_engine, MetaData

engine = create_engine(r'postgresql://geonode:geonode@127.0.0.1/geonode-imports')
metadata = MetaData(engine,schema='public')

try:
    conn = engine.connect()
    conn.execute("SET search_path TO public")
except Exception as e:
    print e.message

table_area = 'sparc_adm2_area_population'
table_pop = 'sparc_annual_pop'

engine = create_engine(r'postgresql://geonode:geonode@127.0.0.1/geonode-imports')
df_pop_area_adm2 = estrazione_dati_da_dbf_dello_shape_e_conversione_pandas()

table_adm2_area_population = 'sparc_adm2_area_population'
#df_pop_area_adm2.to_sql(table_adm2_area_population, engine, schema='public')









