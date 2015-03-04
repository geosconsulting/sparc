# -*- coding: utf-8 -*

import unicodedata
import re
import os
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData,ForeignKey

from osgeo import ogr
ogr.UseExceptions()

import arcpy
arcpy.CheckOutExtension("spatial")

from arcpy import env
env.overwriteOutput = "true"

class ProgettoDrought(object):

    def __init__(self, dbname, user, password):

        self.proj_dir = "c:/data/tools/sparc/projects/"
        self.shape_countries = "c:/data/tools/sparc/input_data/gaul/gaul_wfp_iso.shp"
        self.campo_nome_paese = "ADM0_NAME"
        self.campo_iso_paese = "ADM0_CODE"
        self.campo_nome_admin = "ADM2_NAME"
        self.campo_iso_admin = "ADM2_CODE"

        driver = ogr.GetDriverByName("ESRI Shapefile")
        self.shapefile = driver.Open(self.shape_countries)
        self.layer = self.shapefile.GetLayer()

        self.schema = 'public'
        self.dbname = dbname
        self.user = user
        self.password = password

        try:
            connection_string = "dbname=%s user=%s password=%s" % (self.dbname, self.user, self.password)
            self.conn = psycopg2.connect(connection_string)
            print "Connesso"
        except Exception as e:
            print e.message

        try:
            self.cur = self.conn.cursor()
            print "Cursore attivo"
        except Exception as e:
            print e.message

        #stringa_engine = 'postgresql://geonode:geonode@localhost/geonode-imports'
        self.engine = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports') # , echo=True)
        self.conn = self.engine.connect()
        self.metadata = MetaData(self.engine)

        # if os.path.isfile("C:/data/tools/sparc/input_data/population/" + self.wfp_area + "/" + self.iso3 + "-POP/" + self.iso3 + "10.tif"):
        #     self.population_raster = "C:/data/tools/sparc/input_data/population/" + self.wfp_area + "/" + self.iso3 + "-POP/" + self.iso3 + "10.tif" #popmap10.tif"
        # else:
        #     print "No Population Raster......"
        #     self.population_raster = "None"
        #
        # self.flood_aggregated = "C:/data/tools/sparc/input_data/flood/merged/" + self.paese + "_all_rp_rcl.tif"
        # self.historical_accidents = "C:/data/tools/sparc/input_data/historical_data/floods.csv"
        #
        # if os.path.isfile("C:/data/tools/sparc/input_data/geocoded/risk_map/" + self.paese + ".tif"):
        #     self.risk_raster = "C:/data/tools/sparc/input_data/geocoded/risk_map/" + self.paese + ".tif"
        # else:
        #     self.risk_raster = "None"
        #     print "Risk raster not available...."
        #
        # self.reliability_value = ""

    def creazione_struttura(self,admin_inviata):

        os.chdir(self.proj_dir)
        country_low = str(self.paese).lower()
        if os.path.exists(country_low):
            os.chdir(self.proj_dir + country_low)
            admin_low = admin_inviata.lower()
            if os.path.exists(admin_low):
                pass
            else:
                os.mkdir(admin_low.replace("\n", ""))
        else:
            os.chdir(self.proj_dir)
            os.mkdir(country_low)
            os.chdir(self.proj_dir + country_low)
            admin_low = admin_inviata.lower()
            if os.path.exists(admin_low):
                pass
            else:
                os.mkdir(admin_low.replace("\n", ""))

        #return "Project created......\n"

class HazardAssessmentCountry(ProgettoDrought):

    def estrazione_poly_admin(self):

        #filter_field_name = "ADM2_NAME"
        filter_field_name = "ADM2_CODE"

        # Get the input Layer
        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        inDataSource = inDriver.Open(self.shape_countries, 0)
        inLayer = inDataSource.GetLayer()
        inLayerProj = inLayer.GetSpatialRef()
        #print inLayerProj

        #inLayer.SetAttributeFilter("ADM2_NAME = '" + str(self.admin) + "'")
        print "ADM2_CODE=" + str(self.code)
        inLayer.SetAttributeFilter("ADM2_CODE=" + str(self.code))

        # Create the output LayerS
        outShapefile = os.path.join(self.dirOut + self.admin + ".shp")
        outDriver = ogr.GetDriverByName("ESRI Shapefile")

        # Remove output shapefile if it already exists
        if os.path.exists(outShapefile):
            outDriver.DeleteDataSource(outShapefile)

        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(outShapefile)
        out_lyr_name = (os.path.splitext(os.path.split(outShapefile)[1])[0]).replace("\n","")
        out_layer = outDataSource.CreateLayer(str(out_lyr_name), inLayerProj, geom_type=ogr.wkbMultiPolygon)

        # Add input Layer Fields to the output Layer if it is the one we want
        inLayerDefn = inLayer.GetLayerDefn()
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            fieldName = fieldDefn.GetName()
            if fieldName not in filter_field_name:
                continue
            out_layer.CreateField(fieldDefn)

        # Get the output Layer's Feature Definition
        outLayerDefn = out_layer.GetLayerDefn()

        # Add features to the ouput Layer
        for inFeature in inLayer:
            # Create output Feature
            outFeature = ogr.Feature(outLayerDefn)

            # Add field values from input Layer
            for i in range(0, outLayerDefn.GetFieldCount()):
                fieldDefn = outLayerDefn.GetFieldDefn(i)
                fieldName = fieldDefn.GetName()
                if fieldName not in filter_field_name:
                    continue
                outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(),1)
                    #inFeature.GetField(i))

            # Set geometry as centroid
            geom = inFeature.GetGeometryRef()
            outFeature.SetGeometry(geom.Clone())
            # Add new feature to output Layer
            out_layer.CreateFeature(outFeature)

        # Close DataSources
        inDataSource.Destroy()
        outDataSource.Destroy()
        return "Admin extraction......"

    def conversione_vettore_raster_admin(self):

        global admin_vect
        admin_vect = self.dirOut + self.admin + ".shp"

        global admin_rast
        if len(self.admin) > 5:
            admin = self.admin[0:3]
        admin_rast = self.dirOut + self.admin + "_rst.tif"

        try:
            admin_rast = arcpy.PolygonToRaster_conversion(admin_vect, "ADM2_CODE", admin_rast, "CELL_CENTER", "NONE", 0.0008333)
        except Exception as e:
            print e.message

        return "Raster Created...."

    def taglio_raster_popolazione(self):

        #CUT and SAVE Population within the admin2 area
        if self.population_raster!= "None":
            lscan_out_rst = arcpy.Raster(self.population_raster) * arcpy.Raster(admin_rast)
            lscan_out = self.dirOut + self.admin + "_pop.tif"
            lscan_out_rst.save(lscan_out)
            return "sipop"
        else:
            return "nopop"

    def taglio_raster_inondazione_aggregato(self):

        #CUT and SAVE Flooded areas within the admin2 area
        try:
            flood_out_rst = arcpy.Raster(self.flood_aggregated) * arcpy.Raster(admin_rast)
        except:
            pass
            return "NoFloodRaster"

        flood_out = self.dirOut + self.admin + "_agg.tif"
        flood_out_rst.save(flood_out)
        arcpy.CalculateStatistics_management(flood_out)
        try:
            proprieta = arcpy.GetRasterProperties_management(flood_out, "UNIQUEVALUECOUNT")
            #print proprieta
            return "Flood"
        except:
            pass
            return "NoFlood"

    def calcolo_statistiche_zone_inondazione(self):
        flood_out = arcpy.Raster(self.dirOut + self.admin + "_agg.tif")
        pop_out = arcpy.Raster(self.dirOut + self.admin + "_pop.tif")
        pop_stat_dbf = self.dirOut + self.admin.lower() + "_pop_stat.dbf"
        tab_valori = arcpy.gp.ZonalStatisticsAsTable_sa(flood_out, "Value", pop_out, pop_stat_dbf , "DATA", "ALL")
        return "People in flood prone areas....\n"

class ManagePostgresDB(ProgettoDrought):

    def leggi_paesi(self):

        tab_paesi = Table('sparc_wfp_countries', self.metadata, autoload=True, autoload_with=self.conn, postgresql_ignore_search_path=True)

        s = tab_paesi.select()
        rs = s.execute()
        paesi_dal_db = rs.fetchall()
        paesi = []
        for paese in paesi_dal_db:
            paesi.append(paese[0])

        return paesi

    def leggi_aree_amministrative_paese(self, paese):

        comando = "SELECT adm0_name,iso3,adm1_name,adm1_code,adm2_name,adm2_code FROM sparc_gaul_wfp_iso WHERE adm0_name ='" + paese.strip() + "';"
        #print comando
        admin_paese = self.cur.execute(comando)
        print admin_paese
        return admin_paese


    def check_tabella(self,tabella):

            esiste_tabella = "SELECT '"+ self.schema + "." + tabella + "'::regclass"
            connection_string = "dbname=%s user=%s password=%s" % (self.dbname, self.user,self.password)
            conn_check = psycopg2.connect(connection_string)
            cur_check = conn_check.cursor()

            try:
                cur_check.execute(esiste_tabella)
                return "exists"
            except psycopg2.ProgrammingError as laTabellaNonEsiste:
                #descrizione_errore = laTabellaNonEsiste.pgerror
                codice_errore = laTabellaNonEsiste.pgcode
                #return descrizione_errore, codice_errore
                return codice_errore

            cur_check.close()
            conn_check.close()

    def cancella_tabella(self):

        comando_delete_table = "DROP TABLE " + self.schema + ".sparc_population_month CASCADE;"
        try:
            self.cur.execute(comando_delete_table)
            return "Table deleted"
        except psycopg2.Error as delErrore:
            errore_delete_tabella = delErrore.pgerror
            return errore_delete_tabella

    def create_sparc_population_month(self):

        SQL = "CREATE TABLE %s.%s %s %s;"
        campi = """(
           id serial,
           iso3 character(3),
           adm0_name character(120),
           adm0_code character(8),
           adm1_name character(120),
           adm1_code character(8),
           adm2_code character(8),
           adm2_name character(120),
           rp integer,
           jan integer,
           feb integer,
           mar integer,
           apr integer,
           may integer,
           jun integer,
           jul integer,
           aug integer,
           sep integer,
           oct integer,
           nov integer,
           dec integer,
           n_cases double precision,"""
        constraint = "CONSTRAINT population_month_pkey PRIMARY KEY (id));"

        try:
            comando = SQL % (self.schema, 'sparc_population_month', campi, constraint)
            self.cur.execute(comando)
            print "Monthly Population Split Table Created"
        except psycopg2.Error as createErrore:
            descrizione_errore = createErrore.pgerror
            codice_errore = createErrore.pgcode
            print descrizione_errore, codice_errore

    def inserisci_valori_calcolati(self):

        for linea in lista_finale:
            inserimento = "INSERT INTO " + self.schema + ".sparc_population_month" + \
                          " (iso3, adm0_name,adm0_code,adm1_name,adm1_code,adm2_code,adm2_name," \
                          "rp,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,\"dec\", n_cases)" \
                          "VALUES('" + str(linea[0]) + "','" + linea[1] + "'," + linea[2] + ",'" + linea[3] + "'," \
                                     + linea[4] + "," + linea[5] + ",'" + linea[6] + "'," + linea[7] + "," \
                                     + linea[8] + "," + linea[9] + "," + linea[10] + "," + linea[11] + "," \
                                     + linea[12] + "," + linea[13] + "," + linea[14] + "," + linea[15] + "," \
                                     + linea[16] + "," + linea[17] + "," + linea[18] + "," + linea[19] + "," \
                                     + linea[20] + ");"
            #print inserimento
            self.cur.execute(inserimento)

    def salva_cambi(self):
        try:
            self.conn.commit()
            print "Changes saved"
        except:
            print "Problem in saving data"

    def close_connection(self):
        try:
            self.cur.close()
            self.conn.close()
            print "Connection closed"
        except:
            print "Problem in closing the connection"