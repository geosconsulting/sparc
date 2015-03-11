__author__ = 'fabio.lana'

import os
import sys
from osgeo import ogr
ogr.UseExceptions()

import CompleteProcessingFlood as completeSparc

paese = "India"
dbname = "geonode-imports"
user = "geonode"
password = "geonode"
lista_amministrazioni = None

def processo_dati(paese):

    nome_admin = ''
    code_admin = ''
    processo_controllo = 0

    generazione_di_fenomeni = completeSparc.Progetto(paese, nome_admin, code_admin, dbname, user, password)
    lista_amministrazioni = generazione_di_fenomeni.lista_admin2()[1]

    for aministrazione in lista_amministrazioni.iteritems():

        code_admin = aministrazione[0]
        nome_admin = aministrazione[1]['name_clean']

        generazione_di_fenomeni.livelli_amministrativi_0_1(code_admin)

        generazione_di_fenomeni.creazione_struttura(nome_admin,code_admin)
        newHazardAssessment = completeSparc.HazardAssessmentCountry(paese, nome_admin, code_admin,
                                                                    dbname, user, password)
        newHazardAssessment.estrazione_poly_admin()

        #It is not necessary anymore as I use raster mask
        #newHazardAssessment.conversione_vettore_raster_admin()
        if newHazardAssessment.taglio_raster_popolazione() == "sipop":
            pass
            #print "Population clipped...."
        elif newHazardAssessment.taglio_raster_popolazione() == "nopop":
            print "Population raster not yet released...."
            sys.exit()

        esiste_flood = newHazardAssessment.taglio_raster_inondazione_aggregato()
        if esiste_flood == "Flood":
            newHazardAssessment.calcolo_statistiche_zone_inondazione()
        else:
            pass
        newMonthlyAssessment = completeSparc.MonthlyAssessmentCountry(paese, nome_admin, code_admin,
                                                                      dbname, user, password)
        #newMonthlyAssessment.cut_monthly_precipitation_rasters()
        newMonthlyAssessment.valore_precipitation_reliability_centroid()
        newMonthlyAssessment.analisi_valori_da_normalizzare()
        newMonthlyAssessment.population_flood_prone_areas()

        file_controllo = generazione_di_fenomeni.dirOutPaese + "/" + str(paese) + ".txt"

        if processo_controllo == 0:
            if os.path.isfile(file_controllo):
                os.remove(file_controllo)
        processo_controllo = 1

        newMonthlyAssessment.calcolo_finale(file_controllo)

def scrittura_dati(paese):

    wfp_countries = 'sparc_wfp_countries'
    wfp_areas = 'sparc_wfp_areas'
    gaul_wfp_iso = 'sparc_gaul_wfp_iso' #THIS IS THE GIS TABLE CONTAINING ALL POLYGONS
    nome_admin = ''
    code_admin = ''
    scrittura_tabelle = completeSparc.ManagePostgresDB(paese, nome_admin, code_admin, dbname, user, password)

    if scrittura_tabelle.check_tabella_month() == '42P01':
        scrittura_tabelle.create_sparc_population_month()
        scrittura_tabelle.fetch_results()
        scrittura_tabelle.inserisci_valori_calcolati()

    if scrittura_tabelle.check_tabella_month() == 'exists':
        scrittura_tabelle.fetch_results()
        scrittura_tabelle.inserisci_valori_calcolati()

    if scrittura_tabelle.check_tabella_year() == '42P01':
        scrittura_tabelle.create_sparc_population_annual()
        dct_annuali = scrittura_tabelle.collect_annual_data_byRP_from_dbf_country()
        adms = dct_annuali[2].keys()
        adms_names = [x.split("_")[1] for x in adms]
        scrittura_tabelle.inserisci_valori_dbfs(scrittura_tabelle.process_dct_annuali(adms_names, dct_annuali[2]))

    if scrittura_tabelle.check_tabella_year() == 'exists':
        dct_annuali = scrittura_tabelle.collect_annual_data_byRP_from_dbf_country()
        adms = dct_annuali[2].keys()
        adms_names = [x.split("_")[1] for x in adms]
        scrittura_tabelle.inserisci_valori_dbfs(scrittura_tabelle.process_dct_annuali(adms_names, dct_annuali[2]))

    scrittura_tabelle.salva_cambi()
    scrittura_tabelle.close_connection()
