# -*- coding: utf-8 -*
import dbf
import unicodedata
import re
import os
from osgeo import ogr
ogr.UseExceptions()
import glob
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

        self.drought_monthly_tifs_dir = "C:/data/tools/sparc/input_data/drought/resampled_month/"
        self.drought_seasonal_tifs_dir = "C:/data/tools/sparc/input_data/drought/resampled_seasonal/"

        os.chdir(self.drought_monthly_tifs_dir)
        self.drought_monthly_tifs = glob.glob("*.tif")

        os.chdir(self.drought_seasonal_tifs_dir)
        self.drought_seasonal_tifs = glob.glob("*.tif")

    def admin_2nd_level_list(self, paese):

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
            listone[lista_iso[i]] = {'name_orig': lista_admin2[i], 'name_clean': lista_clean[i]}

        return lista_admin2, listone

    def administrative_level_0_1_fetch(self, code_admin):

        comando = "SELECT iso2,iso3,adm0_code,adm0_name,adm1_name,adm1_code FROM sparc_gaul_wfp_iso WHERE adm2_code=" + \
                  str(code_admin) + ";"
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

    def file_structure_creation(self, admin_name, adm_code):

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


    def extract_poly2_admin(self, paese, name_admin, code):

        filter_field_name = '"' + self.campo_nome_paese + "," + self.campo_iso_paese + "," + self.campo_nome_admin1 + "," + \
                            self.campo_iso_admin1 + "," + self.campo_nome_admin + "," + self.campo_iso_admin + '"'

        # Get the input Layer
        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        inDataSource = inDriver.Open(self.shape_countries, 0)
        inLayer = inDataSource.GetLayer()
        inLayerProj = inLayer.GetSpatialRef()

        inLayer.SetAttributeFilter("ADM2_CODE=" + str(code))

        # Create the output LayerS
        outShapefile = os.path.join(self.proj_dir + paese + "/" + name_admin + "_" + str(code) + "/" + name_admin +
                                    ".shp")
        outDriver = ogr.GetDriverByName("ESRI Shapefile")

        # Remove output shapefile if it already exists
        if os.path.exists(outShapefile):
            outDriver.DeleteDataSource(outShapefile)

        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(outShapefile)
        out_lyr_name = (os.path.splitext(os.path.split(outShapefile)[1])[0]).replace("\n", "")
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

    def statistics_drought_zones(self):

        pop_out = arcpy.Raster(self.lscan_cut_adm2)
        scrivi_qui = arcpy.Describe(pop_out).path
        scrivi_questo = str(pop_out).split("/")[7].split("_")[0]
        # one or both raster could be empty (no flood in polygon) I chech that
        sum_val_pop = int(arcpy.GetRasterProperties_management(pop_out, "UNIQUEVALUECOUNT")[0])
        for dr_temp in self.adm2_drought_months:
            valore_taglio = str(dr_temp.split("/")[-1]).count("_")
            contatore = str(dr_temp.split("/")[-1]).split("_")[valore_taglio].split(".")[0]
            dr_out = arcpy.Raster(dr_temp)
            sum_val_fld = int(arcpy.GetRasterProperties_management(dr_out, "UNIQUEVALUECOUNT")[0])
            nome_tabella = str(scrivi_questo).split("_")[0]
            pop_stat_dbf = scrivi_qui + "/" + nome_tabella + "_" + str(contatore) + "_pop_stat.dbf"
            if sum_val_fld > 0 and sum_val_pop > 0:
                try:
                    arcpy.gp.ZonalStatisticsAsTable_sa(dr_out, "VALUE", pop_out, pop_stat_dbf, "DATA", "SUM")
                except Exception as e:
                    print e.message
            else:
                template_dbf = "C:/data/tools/sparc/input_data/drought/template_pop_stat.dbf"
                tabula = str(scrivi_questo).split("_")[0] + "_" + str(contatore) + "_pop_stat.dbf"
                print "nome tabula %s " % tabula
                try:
                    arcpy.CreateTable_management(scrivi_qui, tabula, template_dbf)
                except Exception as e:
                    print e.message
        return "People in drought areas....\n"

    def cut_rasters_drought(self, paese, name_admin, code):

        global admin_vect
        admin_vect = self.proj_dir + paese + "/" + name_admin + "_" + str(code) + "/" + name_admin + ".shp"

        ProjectDrought.cur = self.conn.cursor()
        comando = "SELECT c.name,c.iso2,c.iso3,a.area_name FROM SPARC_wfp_countries c " \
                  "INNER JOIN SPARC_wfp_areas a " \
                  "ON c.wfp_area = a.area_id WHERE c.name = '" + paese + "';"
        ProjectDrought.cur.execute(comando)
        for row in ProjectDrought.cur:
            self.wfp_area = str(row[3]).strip()
            self.iso3 = row[2]

        if os.path.isfile("C:/data/tools/sparc/input_data/population/" + self.wfp_area + "/" + self.iso3 + "-POP/" + self.iso3 + "13.tif"):
            self.population_raster = "C:/data/tools/sparc/input_data/population/" + self.wfp_area + "/" + self.iso3 + "-POP/" + self.iso3 + "13.tif" #popmap10.tif"
        else:
            print "No Population Raster......"
            self.population_raster = "None"

        #CUT and SAVE Population and Drought Month/Season for each admin2 area
        self.adm2_drought_months = []
        if self.population_raster!= "None":
            # Process: Extract by Mask
            self.lscan_cut_adm2 = self.proj_dir + paese + "/" + name_admin + "_" + str(code) + "/" + name_admin + "_pop.tif"
            try:
                arcpy.gp.ExtractByMask_sa(self.population_raster, admin_vect, self.lscan_cut_adm2)
                contatore = 1
                for raster in self.drought_monthly_tifs:
                    rst_file = self.drought_monthly_tifs_dir + raster
                    try:
                        drought_out = self.proj_dir + paese + "/" + name_admin + "_" + str(code) + "/" + name_admin + "_drmo" + str(contatore) + ".tif"
                        self.adm2_drought_months.append(drought_out)
                        arcpy.gp.ExtractByMask_sa(arcpy.Raster(rst_file), admin_vect, drought_out )
                        contatore += 1
                    except:
                        return "No Drought Raster"
            except:
                return "No Population Raster"
            self.statistics_drought_zones()
        else:
            return "Problem cutting Population Raster"

class ManagePostgresDBDrought(ProjectDrought):

    #########  MONTHLY CALCULATIONS   #########
    #########  MONTHLY CALCULATIONS   #########
    #########  MONTHLY CALCULATIONS   #########

    def check_if_monthly_table_drought_exists(self):

        esiste_tabella = "SELECT '"+ self.schema + ".sparc_population_month_drought'::regclass"
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

    def get_all_administrative_values_using_adm2_code(self):

        cursor = self.conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
        comando = "SELECT c.name,c.iso2,c.iso3,a.area_name FROM SPARC_wfp_countries c INNER JOIN SPARC_wfp_areas a ON c.wfp_area = a.area_id WHERE c.name = '" + self.paese + "';"
        cursor.execute(comando)
        row_count = 0
        for row in cursor:
            row_count += 1
            return row[0], row[1], row[2], row[3]

    def delete_monthly_drought_table_if_exists(self):

        comando_delete_table = "DROP TABLE " + self.schema + ".sparc_population_month_drought CASCADE;"
        try:
            self.cur.execute(comando_delete_table)
            return "Table deleted"
        except psycopg2.Error as delErrore:
            errore_delete_tabella = delErrore.pgerror
            return errore_delete_tabella

    def create_sparc_drought_population_month(self):

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
           month character(3),
           freq integer,
           pop integer,"""
        constraint = "CONSTRAINT pop_month_drought_pkey PRIMARY KEY (id));"

        try:
            comando = SQL % (self.schema, 'sparc_population_month_drought', campi, constraint)
            self.cur.execute(comando)
            print "Monthly Population Drought Table Created"
        except psycopg2.Error as createErrore:
            descrizione_errore = createErrore.pgerror
            codice_errore = createErrore.pgcode
            print descrizione_errore, codice_errore

    def collect_drought_poplation_frequencies_frm_dbfs(self):

        direttorio = self.dirOutPaese

        dct_valori_drought = {}
        for direttorio_principale, direttorio_secondario, file_vuoto in os.walk(direttorio):
            if direttorio_principale != direttorio:
                linea_taglio = 0
                contatore = 0
                for lettera in direttorio_principale:
                    contatore += 1
                    if lettera == '_':
                        linea_taglio = contatore
                admin_name = direttorio_principale[0:linea_taglio-1].split("\\")[1]
                admin_code = direttorio_principale[linea_taglio:]
                files_dbf = glob.glob(direttorio_principale + "/*stat*.dbf")
                for file in files_dbf:
                    solo_file = file.split("\\")[-1]
                    month = os.path.splitext(solo_file)[0].split("_")[1]
                    unique_id = admin_name + "-" + admin_code + "-" + month
                    try:
                        tabella = dbf.Table(file)
                        tabella.open()
                        dct_valori_drought[unique_id] = {}
                        for recordio in tabella:
                            if recordio.value > 0:
                                dct_valori_drought[unique_id][recordio['value']] = recordio['sum']
                    except:
                        pass
        return dct_valori_drought

    def prepare_insert_statements_drought_monthly_values(self,adms, dct_values_annual_drought):

        def associate_raster_to_month(val):

            mese = ''
            if val == 1:
                mese = 'jan'
            elif val == 2:
                mese = 'feb'
            elif val == 3:
                mese = 'mar'
            elif val == 4:
                mese = 'apr'
            elif val == 5:
                mese = 'may'
            elif val == 6:
                mese = 'jun'
            elif val == 7:
                mese = 'jul'
            elif val == 8:
                mese = 'aug'
            elif val == 9:
                mese = 'sep'
            elif val == 10:
                mese = 'oct'
            elif val == 11:
                mese = 'nov'
            elif val == 12:
                mese = 'dec'

            return mese

        schema = 'public'
        dbname = 'geonode-imports'
        user = 'geonode'
        password = 'geonode'

        try:
            connection_string = "dbname=%s user=%s password=%s" % (dbname, user, password)
            conn = psycopg2.connect(connection_string)
        except Exception as e:
            print e.message
        cur = conn.cursor()

        lista = []
        for adm in adms:
            sql = "SELECT DISTINCT iso3, adm0_name, adm0_code, adm1_code,adm1_name, adm2_name, adm2_code FROM " \
                  "sparc_gaul_wfp_iso WHERE adm2_code = '" + str(adm) + "' AND adm0_name = '" + self.paese + "';"
            cur.execute(sql)
            risultati = cur.fetchall()
            lista.append(risultati)

        dct_all_admin_values = {}
        for indice in range(0, len(lista)):
            radice_dct = lista[indice][0][6]
            dct_all_admin_values[radice_dct] = {}
            dct_all_admin_values[radice_dct]["iso3"] = str(lista[indice][0][0].strip())
            dct_all_admin_values[radice_dct]["adm0_name"] = str(lista[indice][0][1].strip())
            dct_all_admin_values[radice_dct]["adm0_code"] = str(lista[indice][0][2])
            dct_all_admin_values[radice_dct]["adm1_code"] = str(lista[indice][0][3])
            dct_all_admin_values[radice_dct]["adm1_name"] = str(lista[indice][0][4].strip())
            dct_all_admin_values[radice_dct]["adm2_name"] = str(lista[indice][0][5].strip())
            dct_all_admin_values[radice_dct]["adm2_code"] = str(lista[indice][0][6])

        linee =[]
        for single_adm_chiavi,single_adm_value in sorted(dct_all_admin_values.iteritems()):
            for adm2_drought_keys, adm2_drought_values in sorted(dct_values_annual_drought.iteritems()):
                val_adm = int(adm2_drought_keys.split("-")[1])
                if single_adm_chiavi == val_adm:
                    month_numeric = int(adm2_drought_keys.split('drmo')[1])
                    month_textual = associate_raster_to_month(month_numeric)
                    linea_adm = str("'" + single_adm_value['iso3']).upper() + "','" + str(single_adm_value['adm0_name']).capitalize() + "'," + single_adm_value['adm0_code'] + \
                               ",'" + str(single_adm_value['adm1_name']).capitalize() + "'," + single_adm_value['adm1_code'] + \
                               "," + single_adm_value['adm2_code'] + ",'" + single_adm_value['adm2_name'] + "'"
                    for linee_con_corrispondenza_amministrativa in dct_values_annual_drought.iteritems():
                        if linee_con_corrispondenza_amministrativa[0] == adm2_drought_keys:
                            if len(linee_con_corrispondenza_amministrativa[1].keys())> 0:
                                for dove_ci_sono_persone in linee_con_corrispondenza_amministrativa[1].iteritems():
                                    linea_calc = "'" + month_textual + "'," + str(dove_ci_sono_persone[0]) + "," + str(dove_ci_sono_persone[1])
                                    linee.append(linea_adm + "," + linea_calc)

        inserimento_mensili = []
        for linea in linee:
            #print linea,len(linea)
            inserimento = "INSERT INTO public.sparc_population_month_drought" + \
                           " (iso3,adm0_name,adm0_code,adm1_name,adm1_code,adm2_code,adm2_name," \
                           "month, freq, pop)" \
                           "VALUES(" + linea + ");"
            #print inserimento
            inserimento_mensili.append(inserimento)

        return lista, dct_all_admin_values ,inserimento_mensili

    def insert_drought_in_postgresql(self, lista_inserimento):

        for ritornato in lista_inserimento:
            #print ritornato
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

    def save_changes(self):
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