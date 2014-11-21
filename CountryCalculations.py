__author__ = 'fabio.lana'

import os
from osgeo import ogr
ogr.UseExceptions()

import CompleteProcessing as completeSparc

paese = "Togo"
dbname = "geonode-imports"
user = "postgres"
password = "antarone"
wfp_area = ''
iso3 = ''
nome_admin = ''
code_admin = ''

generazione_di_fenomeni = completeSparc.Progetto(wfp_area, iso3, paese, nome_admin, code_admin, dbname, user, password)
lista_amministrazioni = generazione_di_fenomeni.lista_admin2()[1]
processo_controllo = 0

def processo_dati():

    # PROCESSO DATI
    for aministrazione in lista_amministrazioni.iteritems():
        code_admin = aministrazione[0]
        nome_admin = aministrazione[1]['name_clean']

        scrittura_db = completeSparc.ManagePostgresDB(wfp_area, iso3, paese, nome_admin, code_admin, dbname, user,
                                                      password)
        nome, iso2, iso3, wfp_area = scrittura_db.leggi_valori_amministrativi()

        nome = str(nome).strip()
        wfp_area = str(wfp_area).strip()
        iso2 = iso2
        iso3 = iso3

        generazione_di_fenomeni.creazione_struttura(nome_admin)
        newHazardAssessment = completeSparc.HazardAssessmentCountry(wfp_area, iso3, paese, nome_admin, code_admin,
                                                                    dbname, user, password)
        newHazardAssessment.estrazione_poly_admin()
        newHazardAssessment.conversione_vettore_raster_admin()
        newHazardAssessment.taglio_raster_popolazione()
        esiste_flood = newHazardAssessment.taglio_raster_inondazione_aggregato()
        if esiste_flood == "Flood":
            newHazardAssessment.calcolo_statistiche_zone_inondazione()
        else:
            pass
        newMonthlyAssessment = completeSparc.MonthlyAssessmentCountry(wfp_area, iso3, paese, nome_admin, code_admin,
                                                                      dbname, user, password)
        newMonthlyAssessment.cut_monthly_rasters()
        newMonthlyAssessment.analisi_valori_da_normalizzare()
        newMonthlyAssessment.population_flood_prone_areas()

        file_controllo = generazione_di_fenomeni.dirOutPaese + "/" + str(paese) + ".txt"
        # print file_controllo
        if processo_controllo == 0:
            if os.path.isfile(file_controllo):
                print "ESISTE"
                os.remove(file_controllo)
        processo_controllo = 1
        newMonthlyAssessment.calcolo_finale(file_controllo)

#processo_dati()

def scrittura_dati():

    wfp_countries = 'sparc_wfp_countries'
    wfp_areas = 'sparc_wfp_areas'
    gaul_wfp_iso = 'sparc_gaul_wfp_iso' #THIS IS THE GIS TABLE CONTAINING ALL POLYGONS
    population_rp = 'sparc_population_rp'
    monthly_prec = 'sparc_monthly_precipitation'
    monthly_prec_norm = 'sparc_monthly_precipitation_norm'
    pop_month = 'sparc_population_month'
    nome_admin = ''
    code_admin = ''
    lista_tabelle = [wfp_countries,wfp_areas,gaul_wfp_iso,population_rp,monthly_prec, monthly_prec_norm, pop_month]
    scrittura_tabelle = completeSparc.ManagePostgresDB(wfp_area, iso3, paese, nome_admin, code_admin,
                                                       dbname, user, password)
    for tabella in lista_tabelle:
        print tabella
        if scrittura_tabelle.check_tabella(tabella)[0:1][0] == '42P01':
            che_tabella = str(scrittura_tabelle.check_tabella(tabella)[1:][0])
            print che_tabella
    #         if che_tabella == 'sparc_population_rp':
    #             scrittura_tabelle.create_sparc_population_rp('sparc_population_rp')
    #             scrittura_tabelle.salva_cambi()
    #         if che_tabella == 'sparc_monthly_precipitation':
    #             scrittura_tabelle.create_sparc_monthly_precipitation('sparc_monthly_precipitation')
    #             scrittura_tabelle.salva_cambi()
    #         if che_tabella == 'sparc_monthly_precipitation_norm':
    #             scrittura_tabelle.create_sparc_monthly_precipitation_norm('sparc_monthly_precipitation_norm')
    #             scrittura_tabelle.salva_cambi()
    #         if scrittura_tabelle == 'sparc_population_month':
    #             scrittura_tabelle.create_sparc_population_month('sparc_population_month')
    #             scrittura_tabelle.salva_cambi()
    # scrittura_tabelle.close_connection()

    # for aministrazione in lista_amministrazioni.iteritems():
    #     code_admin = aministrazione[0]
    #     nome_admin = aministrazione[1]['name_clean']
    #     scrittura_db = completeSparc.ManagePostgresDB(wfp_area, iso3, paese, nome_admin, code_admin,
    #                                                                   dbname, user, password)
    #     scrittura_db.fetch_results()
    #
    #     scrittura_db.salva_cambi()
    #     scrittura_db.close_connection()

scrittura_dati()
