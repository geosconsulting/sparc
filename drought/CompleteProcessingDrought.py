# -*- coding: utf-8 -*
import dbf
import unicodedata
import re
import os
from osgeo import ogr
ogr.UseExceptions()
import glob
import csv
import psycopg2
import psycopg2.extras
import arcpy
arcpy.CheckOutExtension("spatial")
from arcpy import env
env.overwriteOutput = "true"

class ProjectDrought(object):

    def __init__(self, dbname, user, password):

        self.proj_dir = "c:/data/tools/sparc/projects/drought/"
        self.shape_countries = "c:/data/tools/sparc/input_data/gaul/gaul_wfp_iso.shp"
        self.campo_nome_paese = "ADM0_NAME"
        self.campo_iso_paese = "ADM0_CODE"
        self.campo_nome_admin1 = "ADM1_NAME"
        self.campo_iso_admin1 = "ADM1_CODE"
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
        except Exception as e:
            print e.message

        self.cur = self.conn.cursor()

        self.drought_monthly_tifs_dir = "C:/data/tools/sparc/input_data/drought/DSIMonthlyFreq_tiff/"
        self.drought_seasonal_tifs_dir = "C:/data/tools/sparc/input_data/drought/SSNMonthly_tiff/"

        os.chdir(self.drought_monthly_tifs_dir)
        self.drought_monthly_tifs = glob.glob("*.tif")
        #print self.drought_monthly_tifs

        os.chdir(self.drought_seasonal_tifs_dir)
        self.drought_seasonal_tifs = glob.glob("*.tif")
        #print self.drought_seasonal_tifs

    def lista_admin2(self, paese):

        ProjectDrought.paese = paese
        country_capitalized = paese.capitalize()
        self.layer.SetAttributeFilter(self.campo_nome_paese + " = '" + country_capitalized + "'")

        self.dirOutPaese = self.proj_dir + paese

        listone = {}
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

    def livelli_amministrativi_0_1(self, code_admin):

        comando = "SELECT iso2,iso3,adm0_code,adm0_name,adm1_name,adm1_code FROM sparc_gaul_wfp_iso WHERE adm2_code=" + str(code_admin) + ";"
        self.cur.execute(comando)
        for row in self.cur:
            ProjectDrought.ISO2_code = row[0]
            ProjectDrought.ISO3_code = row[1]
            ProjectDrought.ADM0_GAUL_code = row[2]
            ProjectDrought.ADM0_GAUL_name = row[3]
            ProjectDrought.ADM1_GAUL_name = row[4]
            ProjectDrought.ADM1_GAUL_code = row[5]

        dict_all_codes = {}
        dict_all_codes[code_admin] = {}
        dict_all_codes[code_admin]['iso2'] = ProjectDrought.ISO2_code
        dict_all_codes[code_admin]['iso3'] = ProjectDrought.ISO3_code
        dict_all_codes[code_admin]['adm0_code'] = ProjectDrought.ADM0_GAUL_code
        dict_all_codes[code_admin]['adm0_name'] = ProjectDrought.ADM0_GAUL_name
        dict_all_codes[code_admin]['adm1_code'] = ProjectDrought.ADM1_GAUL_code
        dict_all_codes[code_admin]['adm1_name'] = ProjectDrought.ADM1_GAUL_name

        return dict_all_codes

    def creazione_struttura(self, admin_name, adm_code):

        os.chdir(self.proj_dir)
        country_low = str(self.paese).lower()
        if os.path.exists(country_low):
            os.chdir(self.proj_dir + country_low)
            admin_low = admin_name.lower() + "_" + str(adm_code)
            print admin_low
            if os.path.exists(admin_low):
                pass
            else:
                os.mkdir(admin_low.replace("\n", ""))
        else:
            os.chdir(self.proj_dir)
            os.mkdir(country_low)
            os.chdir(self.proj_dir + country_low)
            admin_low = admin_name.lower() + "_" + str(adm_code)
            print admin_low
            if os.path.exists(admin_low):
                pass
            else:
                os.mkdir(admin_low.replace("\n", ""))

        return "Project created......\n"

class HazardAssessmentDrought(ProjectDrought):

    def estrazione_poly_admin(self, paese, name_admin, code):

        filter_field_name = '"' + self.campo_nome_paese + "," + self.campo_iso_paese + "," + self.campo_nome_admin1 + "," + \
                            self.campo_iso_admin1 + "," + self.campo_nome_admin + "," + self.campo_iso_admin + '"'

        # Get the input Layer
        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        inDataSource = inDriver.Open(self.shape_countries, 0)
        inLayer = inDataSource.GetLayer()
        inLayerProj = inLayer.GetSpatialRef()

        inLayer.SetAttributeFilter("ADM2_CODE=" + str(code))

        # Create the output LayerS
        outShapefile = os.path.join(self.proj_dir + paese + "/" + name_admin + "_" + str(code) + "/" + name_admin + ".shp")
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
                dascrivere = inFeature.GetField(fieldName)
                outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), dascrivere)

            # Set geometry as centroid
            geom = inFeature.GetGeometryRef()
            outFeature.SetGeometry(geom.Clone())
            # Add new feature to output Layer
            out_layer.CreateFeature(outFeature)

        # Close DataSources
        inDataSource.Destroy()
        outDataSource.Destroy()
        return "Admin extraction......"

    def cur_rasters(self, paese, name_admin, code):

        global admin_vect
        admin_vect = self.proj_dir + paese + "/" + name_admin + "_" + str(code) + "/" + name_admin + ".shp"
        print admin_vect

        ProjectDrought.cur = self.conn.cursor()
        comando = "SELECT c.name,c.iso2,c.iso3,a.area_name FROM SPARC_wfp_countries c " \
                  "INNER JOIN SPARC_wfp_areas a " \
                  "ON c.wfp_area = a.area_id WHERE c.name = '" + paese + "';"
        ProjectDrought.cur.execute(comando)
        for row in ProjectDrought.cur:
            self.wfp_area = str(row[3]).strip()
            self.iso3 = row[2]

        #print self.wfp_area, self.iso3

        if os.path.isfile("C:/data/tools/sparc/input_data/population/" + self.wfp_area + "/" + self.iso3 + "-POP/" + self.iso3 + "13.tif"):
            self.population_raster = "C:/data/tools/sparc/input_data/population/" + self.wfp_area + "/" + self.iso3 + "-POP/" + self.iso3 + "13.tif" #popmap10.tif"
        else:
            print "No Population Raster......"
            self.population_raster = "None"

        #CUT and SAVE Population within the admin2 area
        if self.population_raster!= "None":
            # Process: Extract by Mask
            lscan_out = self.proj_dir + paese + "/" + name_admin + "_" + str(code) + "/" + name_admin + "_pop.tif"
            arcpy.gp.ExtractByMask_sa(self.population_raster, admin_vect, lscan_out)
            contatore = 1
            for raster in self.drought_monthly_tifs:
                rst_file = self.drought_monthly_tifs_dir + raster
                try:
                    drought_out = self.proj_dir + paese + "/" + name_admin + "_" + str(code) + "/" + name_admin + "_drmo" + str(contatore) + ".tif"
                    print drought_out
                    arcpy.gp.ExtractByMask_sa(arcpy.Raster(rst_file), admin_vect, drought_out )
                    contatore += 1
                except:
                    return "No Drought Raster"
        else:
            return "Raster Problems"

    def calcolo_statistiche_zone_inondazione(self):

        flood_out = arcpy.Raster(self.dirOut + self.admin + "_agg.tif")
        pop_out = arcpy.Raster(self.dirOut + self.admin + "_pop.tif")

        #one or both raster could be empty (no flood in polygon) I chech that
        sum_val_fld = int(arcpy.GetRasterProperties_management(flood_out, "UNIQUEVALUECOUNT")[0])
        sum_val_pop = int(arcpy.GetRasterProperties_management(pop_out, "UNIQUEVALUECOUNT")[0])

        if sum_val_fld > 0 and sum_val_pop > 0:
            pop_stat_dbf = self.dirOut + self.admin.lower() + "_pop_stat.dbf"
            arcpy.gp.ZonalStatisticsAsTable_sa(flood_out, "Value", pop_out, pop_stat_dbf , "DATA", "ALL")
        else:
            template_dbf = "C:/data/tools/sparc/input_data/flood/template_pop_stat.dbf"
            pop_stat_dbf = self.admin.lower() + "_pop_stat.dbf"
            print self.dirOut, pop_stat_dbf
            arcpy.CreateTable_management(self.dirOut, pop_stat_dbf, template_dbf)

        return "People in flood prone areas....\n"

class ManagePostgresDBDrought(ProjectDrought):

    #########  MONTLHY CALCULATIONS   #########
    #########  MONTLHY CALCULATIONS   #########
    #########  MONTLHY CALCULATIONS   #########

    def check_tabella_month(self):

        esiste_tabella = "SELECT '"+ self.schema + ".sparc_population_month'::regclass"
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

    def fetch_results(self):

        global lista_finale
        lista_finale=[]

        with open(self.proj_dir + self.paese + "/" + self.paese + ".txt", 'rb') as csvfile_pop_month:
            pop_monthly_reader = csv.reader(csvfile_pop_month, delimiter=',', quotechar='"')
            for row in pop_monthly_reader:
                lista_finale.append(row)

    def leggi_valori_amministrativi(self):

        cursor = self.conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
        comando = "SELECT c.name,c.iso2,c.iso3,a.area_name FROM SPARC_wfp_countries c INNER JOIN SPARC_wfp_areas a ON c.wfp_area = a.area_id WHERE c.name = '" + self.paese + "';"
        cursor.execute(comando)
        row_count = 0
        for row in cursor:
            row_count += 1
            return row[0], row[1], row[2], row[3]

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

            self.cur.execute(inserimento)

    #########  ANNUAL CALCULATIONS   #########
    #########  ANNUAL CALCULATIONS   #########
    #########  ANNUAL CALCULATIONS   #########

    def check_tabella_year(self):

        esiste_tabella = "SELECT '"+ self.schema + ".sparc_annual_pop'::regclass"
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

    def create_sparc_population_annual(self):

        SQL = "CREATE TABLE %s.%s %s %s;"
        campi = """(
              id serial NOT NULL,
              iso3 character(3),
              adm0_name character(120),
              adm0_code character(12),
              adm1_code character(12),
              adm1_name character(120),
              adm2_code character(12),
              adm2_name character(120),
              rp25 integer,
              rp50 integer,
              rp100 integer,
              rp200 integer,
              rp500 integer,
              rp1000 integer,"""
        constraint = "CONSTRAINT pk_annual_pop PRIMARY KEY (id));"

        try:
            comando = SQL % (self.schema, 'sparc_annual_pop', campi, constraint)
            self.cur.execute(comando)
            print "Annual Population Table Created"
        except psycopg2.Error as createErrore:
            descrizione_errore = createErrore.pgerror
            codice_errore = createErrore.pgcode
            print descrizione_errore, codice_errore

    def collect_annual_data_byRP_from_dbf_country(self):

        contatore_si = 0
        lista_si_dbf = []

        direttorio = self.proj_dir + self.paese
        dct_valori_inondazione_annuale = {}
        for direttorio_principale, direttorio_secondario, file_vuoto in os.walk(direttorio):
            if direttorio_principale != direttorio:
                paese = direttorio_principale.split("/")[5].split("\\")[0]
                admin = direttorio_principale.split(paese)[1][1:]
                files_dbf = glob.glob(direttorio_principale + "/*.dbf")
                for file in files_dbf:
                    fileName, fileExtension = os.path.splitext(file)
                    if 'stat' in fileName:
                        contatore_si += 1
                        lista_si_dbf.append(direttorio_principale)
                        try:
                            filecompleto = fileName + ".dbf"
                            tabella = dbf.Table(filecompleto)
                            tabella.open()
                            dct_valori_inondazione_annuale[admin] = {}
                            for recordio in tabella:
                                if recordio.value > 0:
                                    dct_valori_inondazione_annuale[admin][recordio.value] = recordio.sum
                        except:
                            pass

        lista_stat_dbf = [25, 50, 100, 200, 500, 1000]
        for valore in dct_valori_inondazione_annuale.items():
            quanti_rp = len(valore[1].keys())
            if quanti_rp < 6:
                for rp in lista_stat_dbf:
                    if rp not in valore[1].keys():
                        dct_valori_inondazione_annuale[valore[0]][rp] = 0

        return contatore_si,lista_si_dbf, dct_valori_inondazione_annuale

    def process_dct_annuali(self,adms, dct_valori_inondazione_annuale):

        lista = []
        for adm in adms:
            #print adm
            sql = "SELECT DISTINCT iso3, adm0_name, adm0_code, adm1_code,adm1_name, adm2_name, adm2_code FROM sparc_population_month WHERE adm2_code = '" + adm + "' AND adm0_name = '" + self.paese + "';"
            #print sql
            self.cur.execute(sql)
            risultati = self.cur.fetchall()
            lista.append(risultati)

        dct_valori_amministrativi = {}
        for indice in range(0, len(lista)):
            radice_dct = lista[indice][0][6].strip()
            dct_valori_amministrativi[radice_dct] = {}
            dct_valori_amministrativi[radice_dct]["iso3"] = str(lista[indice][0][0].strip())
            dct_valori_amministrativi[radice_dct]["adm0_name"] = str(lista[indice][0][1].strip())
            dct_valori_amministrativi[radice_dct]["adm0_code"] = str(lista[indice][0][2].strip())
            dct_valori_amministrativi[radice_dct]["adm1_code"] = str(lista[indice][0][3].strip())
            dct_valori_amministrativi[radice_dct]["adm1_name"] = str(lista[indice][0][4].strip())
            dct_valori_amministrativi[radice_dct]["adm2_name"] = str(lista[indice][0][5].strip())
            dct_valori_amministrativi[radice_dct]["adm2_code"] = str(lista[indice][0][6].strip())
        #print dct_valori_amministrativi


        lista_rp = [25, 50, 100, 200, 500, 1000]
        for valore in dct_valori_inondazione_annuale.items():
            quanti_rp = len(valore[1].keys())
            if quanti_rp < 6:
                for rp in lista_rp:
                    if rp not in valore[1].keys():
                        dct_valori_inondazione_annuale[valore[0]][rp] = 0

        linee =[]
        for amministrativa_dct_amministrativi in dct_valori_amministrativi.items():
            adm2_amministrativa = amministrativa_dct_amministrativi[0]
            for amministrativa_dct_inondazione in dct_valori_inondazione_annuale.items():
                if amministrativa_dct_inondazione[0].split("_")[1] == adm2_amministrativa:
                    linee.append(str(amministrativa_dct_amministrativi[1]['iso3']).upper() + "','" + str(amministrativa_dct_amministrativi[1]['adm0_name']).capitalize() + "'," + amministrativa_dct_amministrativi[1]['adm0_code'] +
                                 ",'" + str(amministrativa_dct_amministrativi[1]['adm1_name']).capitalize() + "'," + amministrativa_dct_amministrativi[1]['adm1_code'] +
                                 "," + amministrativa_dct_amministrativi[1]['adm2_code'] + ",'" + adm2_amministrativa +
                                 "'," + str(amministrativa_dct_inondazione[1][25]) + "," + str(amministrativa_dct_inondazione[1][50]) +
                                 "," + str(amministrativa_dct_inondazione[1][100]) + "," + str(amministrativa_dct_inondazione[1][200]) +
                                 "," + str(amministrativa_dct_inondazione[1][500]) + "," + str(amministrativa_dct_inondazione[1][1000]))
        lista_comandi = []
        for linea in linee:
             inserimento = "INSERT INTO " + "public.sparc_annual_pop" + \
                           " (iso3,adm0_name,adm0_code,adm1_name,adm1_code,adm2_code,adm2_name,rp25,rp50,rp100,rp200,rp500,rp1000)" \
                           "VALUES('" + linea + ");"
             lista_comandi.append(inserimento)

        return lista_comandi

    def inserisci_valori_dbfs(self,ritornati_passati):

        for ritornato in ritornati_passati:
            self.cur.execute(ritornato)

    #########  COMMON TASKS   #########
    #########  COMMON TASKS   #########
    #########  COMMON TASKS   #########

    def all_country_db(self):

        self.cur = self.conn.cursor()
        comando = "SELECT DISTINCT adm0_name FROM sparc_gaul_wfp_iso;"

        try:
            self.cur.execute(comando)
        except psycopg2.ProgrammingError as laTabellaNonEsiste:
            descrizione_errore = laTabellaNonEsiste.pgerror
            codice_errore = laTabellaNonEsiste.pgcode
            print descrizione_errore, codice_errore
            return codice_errore

        paesi = []
        for paese in self.cur:
            paesi.append(paese[0])
        return sorted(paesi)

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