#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

from osgeo import ogr

import CompleteProcessingDrought as completeDrought
ogr.UseExceptions()

from Tkinter import *
import ttk

class AppSPARCDrought:

    def __init__(self, master):

        self.paese = "India"
        self.dbname = "geonode-imports"
        self.user = "geonode"
        self.password = "geonode"
        self.lista_amministrazioni = None

        frame = Frame(master, height=32, width=500)
        frame.pack_propagate(0)
        frame.pack()

        self.collect_codes_country_level()
        self.box_value_adm0 = StringVar()
        self.box_adm0 = ttk.Combobox(frame, textvariable= self.box_value_adm0)
        self.box_adm0['values'] = self.lista_paesi
        self.box_adm0.current(0)
        self.box_adm0.pack(side=LEFT)

        self.button = Button(frame, text="Drought Assessment", fg="red", command=self.collect_codes_administrative_level).pack(side=LEFT)

        root = Tk()
        root.title("SPARC Console")
        self.area_messaggi = Text(root, height=15, width=60, background="black", foreground="green")
        self.area_messaggi.pack()

    def collect_codes_country_level(self):

        paesi = completeDrought.ManagePostgresDBDrought(self.dbname, self.user, self.password)
        self.lista_paesi = paesi.all_country_db()

    def collect_codes_administrative_level(self):

        paese = self.box_value_adm0.get()
        self.area_messaggi.delete(1.0, END)

        aree_amministrative = completeDrought.ManagePostgresDBDrought(self.dbname, self.user, self.password)
        lista_admin2 = aree_amministrative.admin_2nd_level_list(paese)

        #print lista_admin2

        for aministrazione in lista_admin2[1].iteritems():

            code_admin = aministrazione[0]
            nome_admin = aministrazione[1]['name_clean']

            all_codes = aree_amministrative.administrative_level_0_1_fetch(code_admin)
            #self.area_messaggi.insert(INSERT, all_codes)

            aree_amministrative.file_structure_creation(nome_admin, code_admin)
            newDroughtAssessment = completeDrought.HazardAssessmentDrought(self.dbname, self.user, self.password)
            newDroughtAssessment.extract_poly2_admin(paese, nome_admin, code_admin)

            section_pop_raster_cut = newDroughtAssessment.cut_rasters_drought(paese,nome_admin, code_admin)

            if section_pop_raster_cut == "sipop":
                print "Population clipped...."
            elif section_pop_raster_cut == "nopop":
                print "Population raster not available...."
                sys.exit()

            # if esiste_flood == "Drougtht":
            #     newDroughtAssessment.calcolo_statistiche_zone_inondazione()
            # else:
            #     pass

    def scrittura_dati(self,paese):

        wfp_countries = 'sparc_wfp_countries'
        wfp_areas = 'sparc_wfp_areas'
        gaul_wfp_iso = 'sparc_gaul_wfp_iso' #THIS IS THE GIS TABLE CONTAINING ALL POLYGONS
        nome_admin = ''
        code_admin = ''
        scrittura_tabelle = completeDrought.ManagePostgresDBDrought(paese, nome_admin, code_admin, dbname, user, password)

        if scrittura_tabelle.check_tabella() == '42P01':
            scrittura_tabelle.create_sparc_drought_population_month()
            #scrittura_tabelle.fetch_results()
            #scrittura_tabelle.inserisci_valori_calcolati()
        if scrittura_tabelle.check_tabella() == 'exists':
            scrittura_tabelle.fetch_results_drought_montly_from_txt_file()
            scrittura_tabelle.insert_monthly_calulated_drought_values()
        scrittura_tabelle.save_changes()
        scrittura_tabelle.close_connection()

    def national_calc_drought(self):

        paese = self.box_value_adm0.get()
        completeDrought.processo_dati(paese)
        completeDrought.scrittura_dati(paese)

root = Tk()
root.title("SPARC Drought Assessment")
app = AppSPARCDrought(root)
root.mainloop()



