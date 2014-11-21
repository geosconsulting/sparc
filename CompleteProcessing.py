# -*- coding: utf-8 -*

import unicodedata
import re
import os
from osgeo import ogr
ogr.UseExceptions()
import glob
import csv
import math
import psycopg2
import psycopg2.extras
import arcpy
arcpy.CheckOutExtension("spatial")
from arcpy import env
env.overwriteOutput = "true"

class Progetto(object):

    def __init__(self, wfp_area,iso3, paese, admin, code, dbname, user, password):

        self.wfp_area = wfp_area
        self.iso3 = iso3
        self.paese = paese
        self.admin = admin
        self.code = code
        self.proj_dir = "c:/data/tools/sparc/projects/"
        self.dirOutPaese = self.proj_dir + paese
        self.dirOut = self.proj_dir + paese + "/" + admin + "/"
        driver = ogr.GetDriverByName("ESRI Shapefile")
        self.shape_countries = "c:/data/tools/sparc/input_data/gaul/gaul_wfp.shp"
        self.campo_nome_paese = "ADM0_NAME"
        self.campo_iso_paese = "ADM0_CODE"
        self.campo_nome_admin = "ADM2_NAME"
        self.campo_iso_admin = "ADM2_CODE"
        self.shapefile = driver.Open(self.shape_countries)
        self.layer = self.shapefile.GetLayer()

        self.schema = 'public'
        self.dbname = dbname
        self.user = user
        self.password = password

        try:
            connection_string = "dbname=%s user=%s password=%s" % (self.dbname, self.user, self.password)
            self.conn = psycopg2.connect(connection_string)
        except Exception as e:
            print e.message

        self.cur = self.conn.cursor()

        self.population_raster = "C:/data/tools/sparc/input_data/population/" + self.wfp_area + "/" + self.iso3 + "-POP/" + self.iso3 + "10.tif" #popmap10.tif"
        self.flood_aggregated = "C:/data/tools/sparc/input_data/flood/merged/" + self.paese + "_all_rp_rcl.tif"
        self.historical_accidents = "C:/data/tools/sparc/input_data/historical_data/floods.csv"

    def lista_admin0(self):
        numFeatures = self.layer.GetFeatureCount()
        lista_stati = []
        for featureNum in range(numFeatures):
            feature = self.layer.GetFeature(featureNum)
            nome_paese = feature.GetField(self.campo_nome_paese)
            lista_stati.append(nome_paese)

        seen = set()
        seen_add = seen.add
        lista_pulita = [x for x in lista_stati if not (x in seen or seen_add(x))]
        lista_admin0 = sorted(lista_pulita)
        return lista_admin0

    def lista_admin2(self):

        country_capitalized = self.paese.capitalize()
        self.layer.SetAttributeFilter(self.campo_nome_paese + " = '" + country_capitalized + "'")

        listone={}
        lista_iso = []
        lista_clean = []
        lista_admin2 = []

        for feature in self.layer:
            cod_admin = feature.GetField(self.campo_iso_admin)
            nome_zozzo = feature.GetField(self.campo_nome_admin)

            unicode_zozzo = nome_zozzo.decode('utf-8')
            nome_per_combo = unicodedata.normalize('NFKD', unicode_zozzo)

            no_dash = re.sub('-', '_', nome_zozzo)
            no_space = re.sub(' ', '', no_dash)
            no_slash = re.sub('/', '_', no_space)
            no_apice = re.sub('\'', '', no_slash)
            no_bad_char = re.sub(r'-/\([^)]*\)', '', no_apice)
            unicode_pulito = no_bad_char.decode('utf-8')
            nome_pulito = unicodedata.normalize('NFKD', unicode_pulito).encode('ascii', 'ignore')

            lista_iso.append(cod_admin)
            lista_clean.append(nome_pulito)
            lista_admin2.append(nome_per_combo)

        for i in range(len(lista_iso)):
            listone[lista_iso[i]] = {'name_orig': lista_admin2[i],'name_clean': lista_clean[i]}

        return lista_admin2, listone

    def creazione_struttura(self,admin_inviata):

        os.chdir(self.proj_dir)
        country_low = str(self.paese).lower()
        if os.path.exists(country_low):
            os.chdir(self.proj_dir + country_low)
            admin_low = admin_inviata.lower()
            if os.path.exists(admin_low):
                pass
            else:
                os.mkdir(admin_low)
        else:
            os.chdir(self.proj_dir)
            os.mkdir(country_low)
            os.chdir(self.proj_dir + country_low)
            admin_low = admin_inviata.lower()
            if os.path.exists(admin_low):
                pass
            else:
                os.mkdir(admin_low)

        #return "Project created......\n"

class HazardAssessmentCountry(Progetto):

    proj_dir = os.getcwd() + "/projects/"
    shape_countries = os.getcwd() + "/input_data/gaul/gaul_wfp.shp"

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
        out_lyr_name = os.path.splitext(os.path.split(outShapefile)[1])[0]
        out_layer = outDataSource.CreateLayer(str(out_lyr_name),inLayerProj, geom_type=ogr.wkbMultiPolygon)

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
        lscan_out_rst = arcpy.Raster(self.population_raster) * arcpy.Raster(admin_rast)
        lscan_out = self.dirOut + self.admin + "_pop.tif"
        lscan_out_rst.save(lscan_out)
        return "Population clipped...."

    def taglio_raster_inondazione_aggregato(self):

        #CUT and SAVE Flooded areas within the admin2 area
        flood_out_rst = arcpy.Raster(self.flood_aggregated) * arcpy.Raster(admin_rast)
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

class MonthlyAssessmentCountry(Progetto):

    monthly_precipitation_dir = "C:/data/tools/sparc/input_data/precipitation/"

    def build_value_list(self,list_val):

        la_lista_finale = {}
        for key, val in list_val.iteritems():
            if key == 'prc01.tif':
                la_lista_finale[1] = val
            elif key == 'prc02.tif':
                la_lista_finale[2] = val
            elif key == 'prc03.tif':
                la_lista_finale[3] = val
            elif key == 'prc04.tif':
                la_lista_finale[4] = val
            elif key == 'prc05.tif':
                la_lista_finale[5] = val
            elif key == 'prc06.tif':
                la_lista_finale[6] = val
            elif key == 'prc07.tif':
                la_lista_finale[7] = val
            elif key == 'prc08.tif':
                la_lista_finale[8] = val
            elif key == 'prc09.tif':
                la_lista_finale[9] = val
            elif key == 'prc10.tif':
                la_lista_finale[10] = val
            elif key == 'prc11.tif':
                la_lista_finale[11] = val
            elif key == 'prc12.tif':
                la_lista_finale[12] = val

        for k, v in la_lista_finale.iteritems():
            if v is None:
                la_lista_finale[k] = 0
        return la_lista_finale

    def cut_monthly_rasters(self):

        os.chdir(self.monthly_precipitation_dir)
        lista_raster = glob.glob("*.tif")
        admin_rast = self.dirOut + self.admin + "_rst.tif"
        #print admin_rast

        valori_mensili = {}
        for raster_mese in lista_raster:
            mese_raster = arcpy.Raster(self.monthly_precipitation_dir + raster_mese)
            mese_tagliato = arcpy.sa.ExtractByRectangle(mese_raster, admin_rast)
            nome = self.dirOut + self.admin + "_" + str(raster_mese)
            mese_tagliato.save(nome)
            valori_mensili[raster_mese] = mese_tagliato.mean

        global dizionario_in
        dizionario_in = self.build_value_list(valori_mensili)
        with open(self.dirOut + self.admin + "_prec.csv", 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for linea in dizionario_in.iteritems():
                csvwriter.writerow(linea)

        global ritornati_somma
        ritornati_somma = sum(dizionario_in.values())

        return "Monthly Probability Function calculated....\n"

    def analisi_valori_da_normalizzare(self):

        mese_di_minimo_valore = min(dizionario_in, key = dizionario_in.get)
        minimo_valore = dizionario_in[mese_di_minimo_valore]
        mese_di_massimo_valore = max(dizionario_in, key = dizionario_in.get)
        massimo_valore = dizionario_in[mese_di_massimo_valore]

        #NORMALIZZAZIONE FATTA A MANO CALCOLANDO TUTTO
        #LO USO PERCHE ALTRIMENTI SI INCASINA LA GENERAZIONE DEI PLOTS
        global normalizzati
        normalizzati = {}
        for linea in dizionario_in.iteritems():
            x_new = (linea[1] - minimo_valore)/(massimo_valore-minimo_valore)
            normalizzati[linea[0]] = x_new

        with open(self.dirOut + self.admin + "_prec_norm.csv", 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for linea in normalizzati.iteritems():
                  csvwriter.writerow(linea)

        return "Monthly Probability Values normalized....\n"

    def historical_analysis_damages(self):

        import collections

        file_incidenti_in = open(self.historical_accidents_file)
        next(file_incidenti_in)
        mesi = []
        for linea in file_incidenti_in:
            splittato_comma = linea.split(",")
            if splittato_comma[2] == self.paese:
                if splittato_comma[0] == 0 or splittato_comma[1] == 0:
                    print splittato_comma[9]
                splittato_mese_inzio = splittato_comma[0].split("/")
                splittato_mese_fine = splittato_comma[1].split("/")
                #print splittato_mese_inzio[1], splittato_mese_fine[1]
                if splittato_mese_inzio[1]!=0 or splittato_mese_fine[0]!=0:
                    differenza = int(splittato_mese_fine[1]) - int(splittato_mese_inzio[1])
                    if differenza == 0:
                         mesi.append(int(splittato_mese_inzio[1]))
                    else:
                        mesi.append(int(splittato_mese_inzio[1]))
                        for illo in range(1, differenza+1):
                            mesi.append(int(splittato_mese_inzio[1]) + illo)
        file_incidenti_in.close()

        conta_mesi = collections.Counter(mesi)
        conta_mesi_ord = collections.OrderedDict(sorted(conta_mesi.items()))

        missing = []
        for indice in range(1, 13):
            if indice not in conta_mesi_ord:
                missing.append(indice)

        for valore in missing:
            conta_mesi_ord[valore] = 0

        global danni_mesi
        danni_mesi = collections.OrderedDict(sorted(conta_mesi_ord.items()))

        return "Monthly subdivision of incidents calculated....\n"

    def population_flood_prone_areas(self):

        global population_in_flood_prone_areas
        try:
            tabella_calcolata = self.dirOut + self.admin + "_pop_stat.dbf"
            tab_cur_pop = arcpy.da.SearchCursor(tabella_calcolata, "*")
            campo_tempo_ritorno = tab_cur_pop.fields.index('Value')
            campo_pop_affected = tab_cur_pop.fields.index('SUM')
            population_in_flood_prone_areas = {}
            for riga_pop in tab_cur_pop:
                tempo_ritorno = riga_pop[campo_tempo_ritorno]
                population_tempo_ritorno = riga_pop[campo_pop_affected]
                if population_tempo_ritorno > 0:
                    population_in_flood_prone_areas[tempo_ritorno] = population_tempo_ritorno
        except:
            pass

        return "Population in flood prone areas calculated....\n"

    def calcolo_finale(self, file_controllo):

        global persone_pesi
        persone_pesi = dict()
        persone_pesi['25'] = {}
        persone_pesi['50'] = {}
        persone_pesi['100'] = {}
        persone_pesi['200'] = {}
        persone_pesi['500'] = {}
        persone_pesi['1000'] = {}

        iteratore = 0
        valori25 = []
        valori50 = []
        valori100 = []
        valori200 = []
        valori500 = []
        valori1000 = []

        #print population_in_flood_prone_areas
        ildizio_chiavi = population_in_flood_prone_areas.keys()
        irps = [25, 50, 100, 200, 500, 1000]
        for chiave in irps:
            if chiave in ildizio_chiavi:
                pass
            else:
                population_in_flood_prone_areas[chiave] = 0

        for persone_chiave, persone_valore in sorted(population_in_flood_prone_areas.iteritems()):
            iteratore += 1
            for peso_chiave, peso_valore in normalizzati.iteritems():
                persone = persone_valore * peso_valore
                if persone_chiave == 25:
                    valori25.append(int(persone))
                    persone_pesi['25'][peso_chiave] = int(persone)
                elif persone_chiave == 50:
                    valori50.append(int(persone))
                    persone_pesi['50'][peso_chiave] = persone
                elif persone_chiave == 100:
                    valori100.append(int(persone))
                    persone_pesi['100'][peso_chiave] = persone
                elif persone_chiave == 200:
                    valori200.append(int(persone))
                    persone_pesi['200'][peso_chiave] = persone
                elif persone_chiave == 500:
                    valori500.append(int(persone))
                    persone_pesi['500'][peso_chiave] = persone
                elif persone_chiave == 1000:
                    valori1000.append(int(persone))
                    persone_pesi['1000'][peso_chiave-1] = persone

        textolio = open(file_controllo, "a")
        textolio.write(str(self.paese) + "," + str(self.code) + "," + str(self.admin) + "," + "25" + "," + str(valori25).replace("[","").replace("]","") + "\n")
        textolio.write(str(self.paese) + "," + str(self.code) + "," + str(self.admin) + "," + "50" + "," + str(valori50).replace("[","").replace("]","") + "\n")
        textolio.write(str(self.paese) + "," + str(self.code) + "," + str(self.admin) + "," + "100" + "," + str(valori100).replace("[","").replace("]","") + "\n")
        textolio.write(str(self.paese) + "," + str(self.code) + "," + str(self.admin) + "," + "200" + "," + str(valori200).replace("[","").replace("]","") + "\n")
        textolio.write(str(self.paese) + "," + str(self.code) + "," + str(self.admin) + "," + "500" + "," + str(valori500).replace("[","").replace("]","") + "\n")
        textolio.write(str(self.paese) + "," + str(self.code) + "," + str(self.admin) + "," + "1000" + "," + str(valori1000).replace("[","").replace("]","") + "\n")
        return "Monthly people divided.....\n"

class ManagePostgresDB(Progetto):

    def fetch_results(self):

        try:
            tabella_popolazione = dbf.Table(self.dirOut + self.admin + "_pop_stat.dbf")
            tabella_popolazione.open()
            print
            print "PEOPLE AT RISK BY RETURN PERIOD " + self.admin
            print
            for linea in tabella_popolazione:
                print "%s %s %s %s %.2f" % (self.paese,self.admin,self.admin_code,linea[0], math.ceil(float(linea[7]/1000.0)))
        except:
            pass

        with open(self.dirOut + self.admin + "_prec.csv", 'rb') as csvfile_prec:
            prec_reader = csv.reader(csvfile_prec, delimiter=' ', quotechar='|')
            print
            print "MM OF RAIN FOR ADMIN 2 " + self.admin
            print
            for row in prec_reader:
                print "%s %s %s %s %.2f" % (self.paese, self.admin, self.code, row[0], math.ceil(float(row[1])/ 1000.0))

        with open(self.dirOut + self.admin + "_prec_norm.csv", 'rb') as csvfile_prec_norm:
            prec_reader_norm = csv.reader(csvfile_prec_norm, delimiter=' ', quotechar='|')
            print
            print "NORMALIZED VALUES FOR RAIN FOR ADMIN 2 " + self.admin
            print
            for row in prec_reader_norm:
                print "%s %s %s %s %.2f" % (self.paese, self.admin, self.code, row[0], math.ceil(float(row[1])/ 1000.0))
                #pass

        with open(self.proj_dir + self.paese + "/" + self.paese + ".txt", 'rb') as csvfile_pop_month:
            pop_monthly_reader = csv.reader(csvfile_pop_month, delimiter=',', quotechar='"')
            for row in pop_monthly_reader:
                print row
                #print "%s %s %s %d" % (row[0],row[2],row[1],int(row[3]))

    def check_tabella(self, tab_check):

        esiste_tabella = "SELECT '"+ self.schema + "." + tab_check + "'::regclass"

        connection_string = "dbname=%s user=%s password=%s" % (self.dbname, self.user,self.password)
        conn_check = psycopg2.connect(connection_string)
        cur_check = conn_check.cursor()

        try:
            cur_check.execute(esiste_tabella)
            return "Table %s exists" % tab_check
        except psycopg2.ProgrammingError as laTabellaNonEsiste:
            #descrizione_errore = laTabellaNonEsiste.pgerror
            codice_errore = laTabellaNonEsiste.pgcode
            #return descrizione_errore, codice_errore
            return codice_errore, tab_check

        cur_check.close()
        conn_check.close()

    def leggi_valori_amministrativi(self):

        cursor = self.conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
        comando = "SELECT c.name,c.iso2,c.iso3,a.area_name FROM SPARC_wfp_countries c INNER JOIN SPARC_wfp_areas a ON c.wfp_area = a.area_id WHERE c.name = '" + self.paese + "';"
        #print comando
        cursor.execute(comando)
        row_count = 0
        for row in cursor:
            row_count += 1
            return (row[0], row[1],row[2],row[3])

    def cancella_tabella(self):

        comando_delete_table = "DROP TABLE " + self.schema + "." + self.tabella_pesi + " CASCADE;"
        try:
            self.cur.execute(comando_delete_table)
            return "Table deleted"
        except psycopg2.Error as delErrore:
            errore_delete_tabella = delErrore.pgerror
            return errore_delete_tabella

    def crea_schema(self):

        SQL = "CREATE SCHEMA %s;"

        try:
            self.cur.execute(SQL % self.schema)
            return "Schema created"
        except psycopg2.Error as createErrore:
            descrizione_errore = createErrore.pgerror
            codice_errore = createErrore.pgcode
            print descrizione_errore,codice_errore
            return descrizione_errore, codice_errore

    def create_sparc_population_rp(self, nome_tabella):

        SQL = "CREATE TABLE %s.%s %s %s;"
        campi = """(
             id serial,
             iso3 character(3),
             adm1_code character(5),
             adm2_code character(5),
             adm2_name character(120),
             pop_25 integer,
             pop_50 integer,
             pop_100 integer,
             pop_150 integer,
             pop_200 integer,
             pop_250 integer,
             pop_500 integer,
             pop_750 integer,
             pop_1000 integer,"""
        constraint = "CONSTRAINT pop_rp_pkey PRIMARY KEY (id))"

        try:
            comando = SQL % (self.schema, nome_tabella, campi, constraint)
            self.cur.execute(comando)
            print "Table Annual Created"
        except psycopg2.Error as createErroreTabellaAnnuale:
            descrizione_errore = createErroreTabellaAnnuale.pgerror
            codice_errore = createErroreTabellaAnnuale.pgcode
            print descrizione_errore, codice_errore

    def create_sparc_monthly_precipitation(self, nome_tabella):

        SQL = "CREATE TABLE %s.%s %s %s;"
        campi = """(
           id serial,
           title character(9),
           jan integer,
           feb integer,
           mar integer,
           apr integer,
           may integer,
           jun integer,
           jul integer,
           ago integer,
           set integer,
           oct integer,
           nov integer,
           dec integer,
           iso3 character(3),
           adm1_code character(5),
           adm2_code character(5),
           adm2_name character(120),"""
        constraint = "CONSTRAINT monthly_prec_pkey PRIMARY KEY (id));"

        try:
            comando = SQL % (self.schema, nome_tabella, campi, constraint)
            self.cur.execute(comando)
            print "Monthly Precipitation Table Created"
        except psycopg2.Error as createErrore:
            descrizione_errore = createErrore.pgerror
            codice_errore = createErrore.pgcode
            print descrizione_errore, codice_errore

    def create_sparc_monthly_precipitation_norm(self, nome_tabella):

        SQL = "CREATE TABLE %s.%s %s %s;"
        campi = """(
           id serial,
           title character(9),
           jan double precision,
           feb double precision,
           mar double precision,
           apr double precision,
           may double precision,
           jun double precision,
           jul double precision,
           ago double precision,
           set double precision,
           oct double precision,
           nov double precision,
           dec double precision,
           iso3 character(3),
           adm1_code character(5),
           adm2_code character(5),
           adm2_name character(120),"""
        constraint = "CONSTRAINT monthly_prec_norm_pkey PRIMARY KEY (id));"

        try:
            comando = SQL % (self.schema, nome_tabella, campi, constraint)
            self.cur.execute(comando)
            print "Monthly Precipitation Normalized Table Created"
        except psycopg2.Error as createErrore:
            descrizione_errore = createErrore.pgerror
            codice_errore = createErrore.pgcode
            print descrizione_errore, codice_errore

    def create_sparc_population_month(self, nome_tabella):

        SQL = "CREATE TABLE %s.%s %s %s;"
        campi = """(
           id serial,
           title character(9),
           jan float,
           feb integer,
           mar integer,
           apr integer,
           may integer,
           jun integer,
           jul integer,
           ago integer,
           set integer,
           oct integer,
           nov integer,
           dec integer,
           iso3 character(3),
           adm1_code character(5),
           adm2_code character(5),
           adm2_name character(120),"""
        constraint = "CONSTRAINT population_month_pkey PRIMARY KEY (id));"

        try:
            comando = SQL % (self.schema, nome_tabella, campi, constraint)
            self.cur.execute(comando)
            print "Monthly Population Split Table Created"
        except psycopg2.Error as createErrore:
            descrizione_errore = createErrore.pgerror
            codice_errore = createErrore.pgcode
            print descrizione_errore, codice_errore

    def inserisci_valori_calcolati(self):
        pass
        # for chiave, valore in val_prec.items():
        #     inserimento = "INSERT INTO " + self.schema + "." + self.nome_tabella + " (month, weight) VALUES (" + str(chiave) + "," + str(valore) + ");"
        #     self.cur.execute(inserimento)

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
