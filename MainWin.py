#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

import CompleteProcessingDrought as completeDrought

from Tkinter import *
import ttk

class AppSPARC:

    def __init__(self, master):

        self.dbname = "geonode-imports"
        self.user = "geonode"
        self.password = "geonode"
        self.lista_amministrazioni = None

        frame = Frame(master, height=32, width=375)
        frame.pack_propagate(0)
        frame.pack()

        self.collect_codes_country_level()
        self.box_value_adm0 = StringVar()
        self.box_adm0 = ttk.Combobox(frame, textvariable = self.box_value_adm0)
        self.box_adm0['values'] = self.lista_paesi
        self.box_adm0.current(0)
        self.box_adm0.pack(side=LEFT)

        self.button = Button(frame, text="Flood Assessment", fg="blue", command=self.national_calc_flood).pack(side=LEFT)
        self.button = Button(frame, text="Drought Assessment", fg="maroon", command=self.national_calc_drought).pack(side=LEFT)


        root = Tk()
        root.title("SPARC Console")
        self.area_messaggi = Text(root, height=15, width=60, background="black", foreground="green")
        self.area_messaggi.pack()

    def collect_codes_country_level(self):

        paesi = completeDrought.ManagePostgresDBDrought(self.dbname, self.user, self.password)
        self.lista_paesi = paesi.all_country_db()

    def national_calc_drought(self):

        paese = self.box_value_adm0.get()

        aree_amministrative = completeDrought.ManagePostgresDBDrought(self.dbname, self.user, self.password)
        lista_admin2 = aree_amministrative.admin_2nd_level_list(paese)

        for aministrazione in lista_admin2[1].iteritems():

            code_admin = aministrazione[0]
            nome_admin = aministrazione[1]['name_clean']

            #all_codes = aree_amministrative.livelli_amministrativi_0_1(code_admin)
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

    def national_calc_flood(self):

        paese = self.box_value_adm0.get()

        import CountryCalculationsFlood
        CountryCalculationsFlood.processo_dati(paese)
        CountryCalculationsFlood.scrittura_dati(paese)

root = Tk()
root.title("SPARC Flood and Drought Assessment")
app = AppSPARC(root)
root.mainloop()



