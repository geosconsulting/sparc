#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

import CompleteProcessingDrought as completeDrought
import UtilitieSparc as us
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

        ut1 = us.UtilitieSparc("India","")
        paesi = ut1.lista_admin0()
        self.box_value_adm0 = StringVar()
        self.box_adm0 = ttk.Combobox(frame, textvariable = self.box_value_adm0)
        self.box_adm0['values'] = paesi
        self.box_adm0.current(0)
        self.box_adm0.pack(side=LEFT)

        self.button = Button(frame, text="Flood Assessment", fg="blue", command=self.national_calc_flood).pack(side=LEFT)
        self.button = Button(frame, text="Drought Assessment", fg="maroon", command=self.national_calc_drought).pack(side=LEFT)


        root = Tk()
        root.title("SPARC Console")
        self.area_messaggi = Text(root, height=15, width=60, background="black", foreground="green")
        self.area_messaggi.pack()

    def national_calc_drought(self):

        paese = self.box_value_adm0.get()
        self.area_messaggi.delete(1.0, END)

        aree_amministrative = completeDrought.ManagePostgresDBDrought(self.dbname, self.user, self.password)
        lista_admin2 = aree_amministrative.lista_admin2(paese)

        #print lista_admin2

        for aministrazione in lista_admin2[1].iteritems():

            code_admin = aministrazione[0]
            nome_admin = aministrazione[1]['name_clean']

            all_codes = aree_amministrative.livelli_amministrativi_0_1(code_admin)
            #self.area_messaggi.insert(INSERT, all_codes)

            aree_amministrative.creazione_struttura(nome_admin, code_admin)
            newDroughtAssessment = completeDrought.HazardAssessmentDrought(self.dbname, self.user, self.password)
            newDroughtAssessment.estrazione_poly_admin(paese, nome_admin, code_admin)

            section_pop_raster_cut = newDroughtAssessment.cur_rasters(paese,nome_admin, code_admin)

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

        import CountryCalculations
        CountryCalculations.processo_dati(paese)
        CountryCalculations.scrittura_dati(paese)

root = Tk()
root.title("SPARC Flood and Drought Assessment")
app = AppSPARC(root)
root.mainloop()



