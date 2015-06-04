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

        self.area_messaggi = Text(finestra, background="black", foreground="green")
        self.area_messaggi.place(x =2, y = 30, width=300, height= 215)

        self.collect_codes_country_level()
        self.box_value_adm0 = StringVar()
        self.box_adm0 = ttk.Combobox(finestra, textvariable = self.box_value_adm0)
        self.box_adm0['values'] = self.lista_paesi
        self.box_adm0.current(0)
        self.box_adm0.place(x = 25 , y = 2, width=210, height=25)

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
        check_all = Checkbutton(finestra, text="All Countries", variable = self.var_check, command=cb)
        check_all.place(x =310, y = 5, width=120, height=25)

        frame_flood = Frame(finestra, height=32, width=400, bg="blue")
        frame_flood.place(x = 305, y = 30, width=140, height=70)

        button_flood = Button(finestra, text="Flood Assessment", fg="blue", command=self.national_calc_flood)
        button_flood.place(x = 310, y = 35, width=130, height=25)

        button_flood_upload = Button(finestra, text="Upload Data Manually", fg="blue", command=self.flood_upload)
        button_flood_upload.place(x = 310, y = 70, width=130, height=25)

        frame_drought = Frame(finestra, height=80, width=400, bg="maroon")
        frame_drought.place(x = 305, y = 105, width=140, height=70)

        button_drought = Button(finestra, text="Drought Assessment", fg="maroon", command=self.national_calc_drought)
        button_drought.place(x = 310, y = 110, width=130, height=25)

        button_drought_upload = Button(finestra, text="Upload Data Manually", fg="maroon", command=self.drought_upload)
        button_drought_upload.place(x = 310, y = 145, width=130, height=25)

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
                self.area_messaggi.insert(INSERT,"Population clipped....")
            elif section_pop_raster_cut == "nopop":
                self.area_messaggi.insert(INSERT,"Population raster not available....")
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
             db_conn_drought.clean_old_values_month_drought(paese)
             db_conn_drought.save_changes()
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

    def drought_upload(self):

        paese = self.box_value_adm0.get()
        import DroughtDataManualUpload as ddup

        proj_dir = "c:/data/tools/sparc/projects/drought/"
        dirOutPaese = proj_dir + paese

        raccogli_da_files_anno = ddup.collect_drought_poplation_frequencies_frm_dbfs(dirOutPaese)
        adms=set()
        for chiave,valori in sorted(raccogli_da_files_anno.iteritems()):
            adms.add(chiave.split("-")[1])
        raccolti_anno = ddup.prepare_insert_statements_drought_monthly_values(paese, adms, raccogli_da_files_anno)
        risultato = ddup.insert_drought_in_postgresql(paese,raccolti_anno[2])
        self.area_messaggi.insert(INSERT,risultato)

    def national_calc_flood(self):

        paese = self.box_value_adm0.get()

        import CountryCalculationsFlood

        calcolo = CountryCalculationsFlood.data_processing_module_flood(paese)
        self.area_messaggi.insert(INSERT, calcolo)

        data_upload  = CountryCalculationsFlood.data_upload_module_flood(paese)
        self.area_messaggi.insert(INSERT, data_upload)

    def world_calc_flood(self):

        paesi = self.box_value_adm0
        for paese in paesi:
            self.box_value_adm0.set(paese)

        # paese = self.box_value_adm0.get()
        # import CountryCalculationsFlood
        # CountryCalculationsFlood.data_processing_module_flood(paese)
        # CountryCalculationsFlood.data_upload_module_flood(paese)

    def flood_upload(self):

        paese = self.box_value_adm0.get()
        import FloodDataManualUpload as fdup

        proj_dir = "c:/data/tools/sparc/projects/floods/"
        dirOutPaese = proj_dir + paese
        fillolo = dirOutPaese + "/" + paese + ".txt"

        raccogli_da_files_anno = fdup.collect_annual_data_byRP_from_dbf_country(dirOutPaese)
        adms = []
        for raccolto in raccogli_da_files_anno:
            adms.append(raccolto)
        raccolti_anno = fdup.process_dict_with_annual_values(paese, adms, raccogli_da_files_anno, fillolo)
        fdup.inserisci_postgresql(paese,raccolti_anno[2])
        raccolti_mese = fdup.raccogli_mensili(fillolo)
        risultato = fdup.inserisci_postgresql(paese,raccolti_mese)
        self.area_messaggi.insert(INSERT, risultato)

root = Tk()
root.title("SPARC Flood and Drought Assessment")
app = AppSPARC(root)




