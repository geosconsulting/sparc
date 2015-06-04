__author__ = 'fabio.lana'
import csv
import os
import glob
import psycopg2
import dbf

def inserisci_postgresql(paese,lista_inserimento):

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

    sql_clean = "DELETE FROM sparc_population_month WHERE adm0_name = '"+ paese + "';"
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

def raccogli_mensili(fillolo):

    lista_finale = []
    with open(fillolo, 'rb') as pop_month:
        pop_monthly_reader = csv.reader(pop_month, delimiter=',', quotechar='"')
        for row in pop_monthly_reader:
            lista_finale.append(row)

    inserimento_mensili = []
    for linea in lista_finale:
        if len(linea) == 21:
            inserimento = "INSERT INTO public.sparc_population_month" + \
                          " (iso3, adm0_name,adm0_code,adm1_name,adm1_code,adm2_code,adm2_name," \
                          "rp,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,\"dec\", n_cases)" \
                          "VALUES('" + str(linea[0]) + "','" + linea[1] + "'," + linea[2] + ",'" + linea[3] + "'," \
                          + linea[4] + "," + linea[5] + ",'" + linea[6] + "'," + linea[7] + "," \
                          + linea[8] + "," + linea[9] + "," + linea[10] + "," + linea[11] + "," \
                          + linea[12] + "," + linea[13] + "," + linea[14] + "," + linea[15] + "," \
                          + linea[16] + "," + linea[17] + "," + linea[18] + "," + linea[19] + "," \
                          + linea[20] + ");"
            inserimento_mensili.append(inserimento)
        else:
            linea_vuota = "0,0,0,0,0,0,0,0,0,0,0,0"
            inserimento = "INSERT INTO public.sparc_population_month" + \
                          " (iso3, adm0_name,adm0_code,adm1_name,adm1_code,adm2_code,adm2_name," \
                          "rp,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,\"dec\", n_cases)" \
                          "VALUES('" + str(linea[0]) + "','" + linea[1] + "'," + linea[2] + ",'" + linea[3] + "'," \
                          + linea[4] + "," + linea[5] + ",'" + linea[6] + "'," + linea[7] + "," \
                          + linea[8] + linea_vuota + "," + linea[9] + ");"
            inserimento_mensili.append(inserimento)

    return inserimento_mensili

def collect_annual_data_byRP_from_dbf_country(direttorio):

    contatore_si = 0
    lista_si_dbf = []

    dct_valori_inondazione_annuale = {}
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
            files_dbf = glob.glob(direttorio_principale + "/*.dbf")
            for file in files_dbf:
                fileName, fileExtension = os.path.splitext(file)
                if 'stat' in fileName:
                    contatore_si += 1
                    lista_si_dbf.append(direttorio_principale)
                    try:
                        tabella = dbf.Table(file)
                        tabella.open()
                        dct_valori_inondazione_annuale[admin_code] = {}
                        dct_valori_inondazione_annuale[admin_code]['adm_name'] = admin_name
                        for recordio in tabella:
                            dct_valori_inondazione_annuale[admin_code]['adm_name'] = admin_name
                            if recordio.value > 0:
                                dct_valori_inondazione_annuale[admin_code][recordio.value] = recordio.sum
                    except:
                        pass

            lista_stat_dbf = [25, 50, 100, 200, 500, 1000]
            for valore in dct_valori_inondazione_annuale.items():
                quanti_rp = len(valore[1].keys())
                if quanti_rp < 6:
                    for rp in lista_stat_dbf:
                        if rp not in valore[1].keys():
                            dct_valori_inondazione_annuale[valore[0]][rp] = 0

    return dct_valori_inondazione_annuale

def process_dict_with_annual_values(paese, adms, dct_valori_inondazione_annuale, file_completo):

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
            sql = "SELECT DISTINCT iso3, adm0_name, adm0_code, adm1_code,adm1_name, adm2_code, adm2_name " \
                  "FROM sparc_gaul_wfp_iso WHERE adm2_code = '" + adm + "' AND adm0_name = '" + paese + "';"

            cur.execute(sql)
            risultati = cur.fetchall()
            lista.append(risultati)

        dct_valori_amministrativi = {}
        for indice in range(0, len(lista)):
            #print lista[indice]
            radice_dct = lista[indice][0][5]
            dct_valori_amministrativi[radice_dct] = {}
            dct_valori_amministrativi[radice_dct]["iso3"] = str(lista[indice][0][0].strip())
            dct_valori_amministrativi[radice_dct]["adm0_name"] = str(lista[indice][0][1].strip())
            dct_valori_amministrativi[radice_dct]["adm0_code"] = str(lista[indice][0][2])
            dct_valori_amministrativi[radice_dct]["adm1_code"] = str(lista[indice][0][3])
            dct_valori_amministrativi[radice_dct]["adm1_name"] = str(lista[indice][0][4].strip())
            dct_valori_amministrativi[radice_dct]["adm2_code"] = str(lista[indice][0][5])
            dct_valori_amministrativi[radice_dct]["adm2_name"] = str(lista[indice][0][6]).strip()

        lista_rp = [25, 50, 100, 200, 500, 1000]
        for valore in dct_valori_inondazione_annuale.items():
            quanti_rp = len(valore[1].keys())
            if quanti_rp < 6:
                for rp in lista_rp:
                    if rp not in valore[1].keys():
                        dct_valori_inondazione_annuale[valore[0]][rp] = 0

        linee =[]
        for amministrativa_dct_amministrativi in dct_valori_amministrativi.items():
            print amministrativa_dct_amministrativi
            adm2_amministrativa = amministrativa_dct_amministrativi[0]
            print adm2_amministrativa
            for amministrativa_dct_inondazione in dct_valori_inondazione_annuale.items():
                #print amministrativa_dct_inondazione[1]['adm_name']
                if int(amministrativa_dct_inondazione[0]) == adm2_amministrativa:
                    try:
                        val25 = amministrativa_dct_inondazione[1][25]
                    except:
                        val25 = 0.0
                    try:
                        val50 = amministrativa_dct_inondazione[1][50]
                    except:
                        val50 = 0.0
                    try:
                        val100 = amministrativa_dct_inondazione[1][100]
                    except:
                        val100 = 0.0
                    try:
                        val200 = amministrativa_dct_inondazione[1][200]
                    except:
                        val200 = 0.0
                    try:
                        val500 = amministrativa_dct_inondazione[1][500]
                    except:
                        val500 = 0.0
                    try:
                        val1000 = amministrativa_dct_inondazione[1][1000]
                    except:
                        val1000 = 0

                    comando = str(amministrativa_dct_amministrativi[1]['iso3']).upper() + "','" + str(amministrativa_dct_amministrativi[1]['adm0_name']).capitalize() + "'," + amministrativa_dct_amministrativi[1]['adm0_code'] + \
                            ",'" + str(amministrativa_dct_amministrativi[1]['adm1_name']).capitalize() + "'," + amministrativa_dct_amministrativi[1]['adm1_code'] + \
                            "," + amministrativa_dct_amministrativi[1]['adm2_code'] + ",'" + str(amministrativa_dct_amministrativi[1]['adm2_name']) + \
                            "'," + str(val25) + "," + str(val50) + "," + str(val100) + "," + str(val200) + "," + str(val500) + "," + str(val1000)
                    linee.append(comando)

        lista_comandi = []
        for linea in linee:
            print linea
            inserimento = "INSERT INTO " + "public.sparc_annual_pop" + \
                " (iso3,adm0_name,adm0_code,adm1_name,adm1_code,adm2_code,adm2_name,rp25,rp50,rp100,rp200,rp500,rp1000)" \
                "VALUES('" + linea + ");"
            lista_comandi.append(inserimento)

        return lista, dct_valori_amministrativi, lista_comandi

# paese = 'Benin'
# proj_dir = "c:/data/tools/sparc/projects/floods/"
# dirOutPaese = proj_dir + paese
# fillolo = dirOutPaese + "/" + paese + ".txt"
#
# raccogli_da_files_anno = collect_annual_data_byRP_from_dbf_country(dirOutPaese)
# adms = []
# for raccolto in raccogli_da_files_anno:
#     adms.append(raccolto)
# raccolti_anno = process_dict_with_annual_values(paese, adms, raccogli_da_files_anno, fillolo)
# inserisci_postgresql(raccolti_anno[2])
#
# raccolti_mese = raccogli_mensili(fillolo)
# inserisci_postgresql(raccolti_mese)
