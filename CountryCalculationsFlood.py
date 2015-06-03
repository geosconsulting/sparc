__author__ = 'fabio.lana'

import os
import sys
from osgeo import ogr
ogr.UseExceptions()

from Tkinter import *
import ttk

import CompleteProcessingFlood as completeSparc

paese = "India"
dbname = "geonode-imports"
user = "geonode"
password = "geonode"
lista_amministrazioni = None

def data_processing_module_flood(paese):

    nome_admin = ''
    code_admin = ''
    processo_controllo = 0

    generazione_di_fenomeni = completeSparc.Progetto(paese, nome_admin, code_admin, dbname, user, password)
    lista_amministrazioni = generazione_di_fenomeni.lista_admin2()[1]

    for aministrazione in lista_amministrazioni.iteritems():

        code_admin = aministrazione[0]
        nome_admin = aministrazione[1]['name_clean']
        generazione_di_fenomeni.livelli_amministrativi_0_1(code_admin)
        generazione_di_fenomeni.creazione_struttura(nome_admin, code_admin)
        newHazardAssessment = completeSparc.HazardAssessmentCountryFlood(paese, nome_admin, code_admin,
                                                                    dbname, user, password)
        newHazardAssessment.estrazione_poly_admin()

        #It is not necessary anymore as I use raster mask
        #newHazardAssessment.conversione_vettore_raster_admin()
        if newHazardAssessment.taglio_raster_popolazione() == "sipop":
            pass
            #print "Population clipped...."
        elif newHazardAssessment.taglio_raster_popolazione() == "nopop":
            print "Population raster not yet released...."
            return "Population data not available...."
            sys.exit()

        esiste_flood = newHazardAssessment.taglio_raster_inondazione_aggregato()
        if esiste_flood == "Flood":
            newHazardAssessment.calcolo_statistiche_zone_inondazione()
        else:
            pass
        newMonthlyAssessment = completeSparc.MonthlyAssessmentCountryFlood(paese, nome_admin, code_admin,
                                                                      dbname, user, password)
        #newMonthlyAssessment.cut_monthly_precipitation_rasters()
        newMonthlyAssessment.valore_precipitation_reliability_centroid()
        newMonthlyAssessment.analisi_valori_da_normalizzare()
        newMonthlyAssessment.population_flood_prone_areas()

        file_controllo = generazione_di_fenomeni.dirOutPaese + "/" + str(paese) + ".txt"
        #print file_controllo
        if processo_controllo == 0:
            if os.path.isfile(file_controllo):
                os.remove(file_controllo)
        processo_controllo = 1

        newMonthlyAssessment.calcolo_finale(file_controllo)

    return "Flood Hazard Calculation Terminated....\n"

def data_upload_module_flood(paese):

    wfp_countries = 'sparc_wfp_countries'
    wfp_areas = 'sparc_wfp_areas'
    gaul_wfp_iso = 'sparc_gaul_wfp_iso' #THIS IS THE GIS TABLE CONTAINING ALL POLYGONS
    nome_admin = ''
    code_admin = ''
    scrittura_tabelle = completeSparc.ManagePostgresDB(paese, nome_admin, code_admin, dbname, user, password)

    if scrittura_tabelle.check_tabella_month() == '42P01':
        scrittura_tabelle.create_sparc_population_month()
        scrittura_tabelle.fetch_results()
        sql_command_list_month = scrittura_tabelle.collect_people_at_risk_montlhy_from_txt()
        scrittura_tabelle.insert_values_in_postgres(sql_command_list_month)

    if scrittura_tabelle.check_tabella_month() == 'exists':
        scrittura_tabelle.clean_old_values_month(paese)
        scrittura_tabelle.save_changes_in_postgres()
        scrittura_tabelle.fetch_results()
        sql_command_list_month = scrittura_tabelle.collect_people_at_risk_montlhy_from_txt()
        scrittura_tabelle.insert_values_in_postgres(sql_command_list_month)

    if scrittura_tabelle.check_tabella_year() == '42P01':
        scrittura_tabelle.create_sparc_population_annual()
        dct_annuali = scrittura_tabelle.collect_annual_data_byRP_from_dbf_country()
        adms = []
        for raccolto in dct_annuali:
            adms.append(raccolto)
        sql_command_list_annual = scrittura_tabelle.process_dict_with_annual_values(adms, dct_annuali)
        scrittura_tabelle.insert_values_in_postgres(sql_command_list_annual[2])

    if scrittura_tabelle.check_tabella_year() == 'exists':
        scrittura_tabelle.clean_old_values_year(paese)
        scrittura_tabelle.save_changes_in_postgres()
        dct_annuali = scrittura_tabelle.collect_annual_data_byRP_from_dbf_country()
        adms = []
        for raccolto in dct_annuali:
            adms.append(raccolto)
        sql_command_list_annual = scrittura_tabelle.process_dict_with_annual_values(adms, dct_annuali)
        scrittura_tabelle.insert_values_in_postgres(sql_command_list_annual[2])

    scrittura_tabelle.save_changes_in_postgres()
    scrittura_tabelle.close_connection_with_postgres()

    return "Flood Hazard Data Uploaded....\n"
