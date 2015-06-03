#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

import CompleteProcessingDrought as completeDrought

from Tkinter import *
import ttk

class AppSPARC:

    def __init__(self, finestra):

        self.dbname = "geonode-imports"
        self.user = "geonode"
        self.password = "geonode"
        self.lista_amministrazioni = None

        finestra.geometry("450x250+30+30")

        self.collect_codes_country_level()
        self.box_value_adm0 = StringVar()
        self.box_adm0 = ttk.Combobox(finestra, textvariable = self.box_value_adm0)
        self.box_adm0['values'] = self.lista_paesi
        self.box_adm0.current(0)
        self.box_adm0.place(x = 2 , y = 2, width=195, height=25)

        def cb():
            attivo_nonAttivo = self.var_check.get()
            print attivo_nonAttivo
            if attivo_nonAttivo == 0:
                self.box_adm0.config(state='normal')
                command_flood = "flood per paese"
                command_drought = "drought per paese"
            else:
                self.box_adm0.config(state='disabled')
                command_flood = "flood per mondo"
                command_drought = "drought per mondo"

        self.var_check = IntVar()

        button_flood = Button(finestra, text="Flood Assessment", fg="blue", command=self.national_calc_flood)
        button_flood.place(x = 200, y = 2, width=120, height=25)

        button_drought = Button(finestra, text="Drought Assessment", fg="maroon", command=self.national_calc_drought)
        button_drought.place(x =325, y = 2, width=120, height=25)

        check_all = Checkbutton(finestra, text="All Countries", variable = self.var_check, command=cb)
        check_all.place(x =10, y = 28, width=120, height=25)

        self.area_messaggi = Text(finestra, background="black", foreground="green")
        self.area_messaggi.place(x =2, y = 50, width=445, height= 198)

        finestra.mainloop()

    def collect_codes_country_level(self):

        paesi = completeDrought.ManagePostgresDBDrought(self.dbname, self.user, self.password)
        self.lista_paesi = paesi.all_country_db()

    def national_calc_drought(self):

        paese = self.box_value_adm0.get()

        db_conn_drought = completeDrought.ManagePostgresDBDrought(self.dbname, self.user, self.password)
        lista_admin2 = db_conn_drought.admin_2nd_level_list(paese)

        for aministrazione in lista_admin2[1].iteritems():

            code_admin = aministrazione[0]
            nome_admin = aministrazione[1]['name_clean']

            #all_codes = aree_amministrative.livelli_amministrativi_0_1(code_admin)
            #self.area_messaggi.insert(INSERT, all_codes)

            db_conn_drought.file_structure_creation(nome_admin, code_admin)
            newDroughtAssessment = completeDrought.HazardAssessmentDrought(self.dbname, self.user, self.password)
            newDroughtAssessment.extract_poly2_admin(paese, nome_admin, code_admin)

            section_pop_raster_cut = newDroughtAssessment.cut_rasters_drought(paese,nome_admin, code_admin)

            if section_pop_raster_cut == "sipop":
                print "Population clipped...."
            elif section_pop_raster_cut == "nopop":
                print "Population raster not available...."
                sys.exit()

        dizio_drought = db_conn_drought.collect_drought_population_frequencies_frm_dbfs()
        self.area_messaggi.insert(INSERT, "Data Collected\n")
        adms = set()
        for chiave,valori in sorted(dizio_drought.iteritems()):
            adms.add(chiave.split("-")[1])
        insert_list = db_conn_drought.prepare_insert_statements_drought_monthly_values(adms, dizio_drought)[2]
        self.area_messaggi.insert(INSERT, "Data Ready for Upload in DB\n")

        if db_conn_drought.check_if_monthly_table_drought_exists() == '42P01':
            db_conn_drought.create_sparc_drought_population_month()
            db_conn_drought.insert_drought_in_postgresql(insert_list)

        if db_conn_drought.check_if_monthly_table_drought_exists() == 'exists':
             self.area_messaggi.insert(INSERT, "Table Drought Exist\n")
             db_conn_drought.insert_drought_in_postgresql(insert_list)

        db_conn_drought.save_changes()
        db_conn_drought.close_connection()
        self.area_messaggi.insert(INSERT, "Data for " + paese + " Uploaded in DB")

    def world_calc_drought(self):

        for paese in self.lista_paesi:

            db_conn_drought = completeDrought.ManagePostgresDBDrought(self.dbname, self.user, self.password)
            lista_admin2 = db_conn_drought.admin_2nd_level_list(paese)

            for aministrazione in lista_admin2[1].iteritems():

                code_admin = aministrazione[0]
                nome_admin = aministrazione[1]['name_clean']

                #all_codes = aree_amministrative.livelli_amministrativi_0_1(code_admin)
                #self.area_messaggi.insert(INSERT, all_codes)

                db_conn_drought.file_structure_creation(nome_admin, code_admin)
                newDroughtAssessment = completeDrought.HazardAssessmentDrought(self.dbname, self.user, self.password)
                newDroughtAssessment.extract_poly2_admin(paese, nome_admin, code_admin)

                section_pop_raster_cut = newDroughtAssessment.cut_rasters_drought(paese,nome_admin, code_admin)

                if section_pop_raster_cut == "sipop":
                    print "Population clipped...."
                elif section_pop_raster_cut == "nopop":
                    print "Population raster not available...."
                    sys.exit()

            dizio_drought = db_conn_drought.collect_drought_population_frequencies_frm_dbfs()
            self.area_messaggi.insert(INSERT, "Data Collected\n")
            adms = set()
            for chiave,valori in sorted(dizio_drought.iteritems()):
                adms.add(chiave.split("-")[1])
            insert_list = db_conn_drought.prepare_insert_statements_drought_monthly_values(adms, dizio_drought)[2]
            self.area_messaggi.insert(INSERT, "Data Ready for Upload in DB\n")

            if db_conn_drought.check_if_monthly_table_drought_exists() == '42P01':
                db_conn_drought.create_sparc_drought_population_month()
                db_conn_drought.insert_drought_in_postgresql(insert_list)

            if db_conn_drought.check_if_monthly_table_drought_exists() == 'exists':
                 db_conn_drought.insert_drought_in_postgresql(insert_list)

            db_conn_drought.save_changes()
            db_conn_drought.close_connection()
            self.area_messaggi.insert(INSERT, "Data for " + paese + " Uploaded in DB")

    def national_calc_flood(self):

        paese = self.box_value_adm0.get()

        import CountryCalculationsFlood

        calcolo = CountryCalculationsFlood.data_processing_module_flood(paese)
        self.area_messaggi.insert(INSERT, calcolo)

        data_upload  = CountryCalculationsFlood.data_upload_module_flood(paese)
        self.area_messaggi.insert(INSERT, data_upload)

    def world_calc_flood(self):

        paese = self.box_value_adm0.get()
        import CountryCalculationsFlood
        CountryCalculationsFlood.data_processing_module_flood(paese)
        CountryCalculationsFlood.data_upload_module_flood(paese)

root = Tk()
root.title("SPARC Flood and Drought Assessment")
app = AppSPARC(root)




