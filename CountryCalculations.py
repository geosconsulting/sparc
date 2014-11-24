__author__ = 'fabio.lana'

import os
from osgeo import ogr
ogr.UseExceptions()

import CompleteProcessing as completeSparc

paese = "Benin"
dbname = "geonode-imports"
user = "postgres"
password = "antarone"
wfp_area = ''
iso3 = ''
nome_admin = ''
code_admin = ''

generazione_di_fenomeni = completeSparc.Progetto(paese, nome_admin, code_admin, dbname, user, password)
lista_amministrazioni = generazione_di_fenomeni.lista_admin2()[1]

def processo_dati():

    processo_controllo = 0
    # PROCESSO DATI
    for aministrazione in lista_amministrazioni.iteritems():

        code_admin = aministrazione[0]
        nome_admin = aministrazione[1]['name_clean']

        generazione_di_fenomeni.livelli_amministrativi_0_1(code_admin)

        generazione_di_fenomeni.creazione_struttura(nome_admin)
        newHazardAssessment = completeSparc.HazardAssessmentCountry(paese, nome_admin, code_admin,
                                                                    dbname, user, password)
        newHazardAssessment.estrazione_poly_admin()
        newHazardAssessment.conversione_vettore_raster_admin()
        newHazardAssessment.taglio_raster_popolazione()
        esiste_flood = newHazardAssessment.taglio_raster_inondazione_aggregato()
        if esiste_flood == "Flood":
            newHazardAssessment.calcolo_statistiche_zone_inondazione()
        else:
            pass
        newMonthlyAssessment = completeSparc.MonthlyAssessmentCountry(paese, nome_admin, code_admin,
                                                                      dbname, user, password)
        newMonthlyAssessment.cut_monthly_rasters()
        newMonthlyAssessment.analisi_valori_da_normalizzare()
        newMonthlyAssessment.population_flood_prone_areas()

        file_controllo = generazione_di_fenomeni.dirOutPaese + "/" + str(paese) + ".txt"

        if processo_controllo == 0:
            if os.path.isfile(file_controllo):
                print "ESISTE"
                os.remove(file_controllo)
        processo_controllo = 1

        newMonthlyAssessment.calcolo_finale(file_controllo)
processo_dati()

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
        if scrittura_tabelle.check_tabella(tabella)[0:1][0] == '42P01':
            che_tabella = str(scrittura_tabelle.check_tabella(tabella)[1:][0])
            print che_tabella
            if che_tabella == 'sparc_population_rp':
                scrittura_tabelle.create_sparc_population_rp(che_tabella)
                scrittura_tabelle.salva_cambi()
            if che_tabella == 'sparc_monthly_precipitation':
                scrittura_tabelle.create_sparc_monthly_precipitation(che_tabella)
                scrittura_tabelle.salva_cambi()
            if che_tabella == 'sparc_monthly_precipitation_norm':
                scrittura_tabelle.create_sparc_monthly_precipitation_norm(che_tabella)
                scrittura_tabelle.salva_cambi()
            if che_tabella == 'sparc_population_month':
                scrittura_tabelle.create_sparc_population_month(che_tabella)
                scrittura_tabelle.salva_cambi()
    scrittura_tabelle.close_connection()

    # for aministrazione in lista_amministrazioni.iteritems():
    #     code_admin = aministrazione[0]
    #     nome_admin = aministrazione[1]['name_clean']
    #     scrittura_db = completeSparc.ManagePostgresDB(wfp_area, iso3, paese, nome_admin, code_admin,
    #                                                                   dbname, user, password)
    #     scrittura_db.fetch_results()
    #
    #     scrittura_db.salva_cambi()
    #     scrittura_db.close_connection()
#scrittura_dati()
