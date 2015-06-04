__author__ = 'fabio.lana'
import csv
import os
import glob
import psycopg2
import dbf

def insert_drought_in_postgresql(paese,lista_inserimento):

    schema = 'public'
    dbname = 'geonode-imports'
    user = 'geonode'
    password = 'geonode'

    try:
        connection_string = "dbname=%s user=%s password=%s" % (dbname, user, password)
        conn = psycopg2.connect(connection_string)
    except Exception as e:
        return e.message
    cur = conn.cursor()

    sql_clean = "DELETE FROM sparc_population_month_drought WHERE adm0_name = '"+ paese + "';"
    cur.execute(sql_clean)
    conn.commit()

    for inserimento_singolo in lista_inserimento:
        cur.execute(inserimento_singolo)

    try:
        conn.commit()
    except:
        return "Problem in saving data"

    try:
        cur.close()
        conn.close()
    except:
        return "Problem in closing the connection"

    return "Data have been uploaded...\n"

def collect_drought_poplation_frequencies_frm_dbfs(direttorio):

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
                #print unique_id
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

def prepare_insert_statements_drought_monthly_values(paese, adms, dct_values_annual_drought):

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
            return e.message
        cur = conn.cursor()

        lista = []
        for adm in adms:
            sql = "SELECT DISTINCT iso3, adm0_name, adm0_code, adm1_code,adm1_name, adm2_name, adm2_code FROM " \
                  "sparc_gaul_wfp_iso WHERE adm2_code = '" + adm + "' AND adm0_name = '" + paese + "';"
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

        return lista, dct_all_admin_values,inserimento_mensili

# paese = 'Benin'
# proj_dir = "c:/data/tools/sparc/projects/drought/"
# dirOutPaese = proj_dir + paese
#
# raccogli_da_files_anno = collect_drought_poplation_frequencies_frm_dbfs(dirOutPaese)
# adms=set()
# for chiave,valori in sorted(raccogli_da_files_anno.iteritems()):
#     adms.add(chiave.split("-")[1])
# raccolti_anno = prepare_insert_statements_drought_monthly_values(paese, adms, raccogli_da_files_anno)
# insert_drought_in_postgresql(raccolti_anno[2])
