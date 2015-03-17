__author__ = 'fabio.lana'
import csv
import os
import glob
import psycopg2
import dbf

def inserisci_postgresql(lista_inserimento):

    schema = 'public'
    dbname = 'geonode-imports'
    user = 'geonode'
    password = 'geonode'

    try:
        connection_string = "dbname=%s user=%s password=%s" % (dbname, user, password)
        conn = psycopg2.connect(connection_string)
        print "Connection opened"
    except Exception as e:
        print e.message
    cur = conn.cursor()

    for inserimento_singolo in lista_inserimento:
        #print inserimento_singolo
        cur.execute(inserimento_singolo)

    try:
        conn.commit()
        print "Changes saved"
    except:
        print "Problem in saving data"

    try:
        cur.close()
        conn.close()
        print "Connection closed"
    except:
        print "Problem in closing the connection"

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
                        #TODO: E' qui che devo verificare se raccolgo tutti i valori per ognuno dei 12 raster di drought
                        #TODO: sembra che i valori vengano raccolti ma devo verificare se effettivamente li raccolgo tutti
                        if recordio.value > 0:
                            dct_valori_drought[unique_id][recordio['value']] = recordio['sum']
                except:
                    pass
    return dct_valori_drought

def prepare_insert_statements_drought_monthly_values(paese, adms, dct_values_annual_drought):

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
            sql = "SELECT DISTINCT iso3, adm0_name, adm0_code, adm1_code,adm1_name, adm2_name, adm2_code FROM sparc_gaul_wfp_iso WHERE adm2_code = '" + adm + "' AND adm0_name = '" + paese + "';"
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
        for single_adm_value in dct_all_admin_values.items():
             adm2_code = single_adm_value[0]
             for adm2_drought_keys,adm2_drought_values in sorted(dct_values_annual_drought.iteritems()):
                 print adm2_drought_keys.split("-")[1],adm2_code
                 if adm2_drought_keys.split("-")[1] == adm2_code:
                    linee.append(str(single_adm_value[1]['iso3']).upper() + "','" + str(single_adm_value[1]['adm0_name']).capitalize() + "'," + single_adm_value[1]['adm0_code'] +
                             ",'" + str(single_adm_value[1]['adm1_name']).capitalize() + "'," + single_adm_value[1]['adm1_code'] +
                             "," + single_adm_value[1]['adm2_code'] + ",'" + str(adm2_drought_values))

        #inserimento_mensili = []
        #for linea in lista:
            #print linea
            # if len(linea) == 21:
            #     inserimento = "INSERT INTO public.sparc_population_month_drought" + \
            #               " (iso3, adm0_name,adm0_code,adm1_name,adm1_code,adm2_code,adm2_name," \
            #               "rp,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,\"dec\", n_cases)" \
            #               "VALUES('" + str(linea[0]) + "','" + linea[1] + "'," + linea[2] + ",'" + linea[3] + "'," \
            #               + linea[4] + "," + linea[5] + ",'" + linea[6] + "'," + linea[7] + "," \
            #               + linea[8] + "," + linea[9] + "," + linea[10] + "," + linea[11] + "," \
            #               + linea[12] + "," + linea[13] + "," + linea[14] + "," + linea[15] + "," \
            #               + linea[16] + "," + linea[17] + "," + linea[18] + "," + linea[19] + "," \
            #               + linea[20] + ");"
            #     inserimento_mensili.append(inserimento)
            # else:
            #     linea_vuota = "0,0,0,0,0,0,0,0,0,0,0,0"
            #     inserimento = "INSERT INTO public.sparc_population_month_drought" + \
            #               " (iso3, adm0_name,adm0_code,adm1_name,adm1_code,adm2_code,adm2_name," \
            #               "rp,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,\"dec\", n_cases)" \
            #               "VALUES('" + str(linea[0]) + "','" + linea[1] + "'," + linea[2] + ",'" + linea[3] + "'," \
            #               + linea[4] + "," + linea[5] + ",'" + linea[6] + "'," + linea[7] + "," \
            #               + linea[8] + linea_vuota + "," + linea[9] + ");"
            #     inserimento_mensili.append(inserimento)

        return lista, dct_all_admin_values#, inserimento_mensili

paese = 'Benin'
proj_dir = "c:/data/tools/sparc/projects/drought/"
dirOutPaese = proj_dir + paese

raccogli_da_files_anno = collect_drought_poplation_frequencies_frm_dbfs(dirOutPaese)
adms=set()
for chiave,valori in sorted(raccogli_da_files_anno.iteritems()):
    adms.add(chiave.split("-")[1])
raccolti_anno = prepare_insert_statements_drought_monthly_values(paese, adms, raccogli_da_files_anno)

#print raccolti_anno
#inserisci_postgresql(raccolti_anno[2])

#inserisci_postgresql(raccolti_mese)