#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

from Tkinter import *
import ttk

from interfaces_discontinued import HazardAssessment as ha
import MonthlyDistribution as monDist
import intermedi.interfaces_discontinued.UtilitieSparc as us


class AppSPARC:

    def __init__(self, master):

        frame = Frame(master, height=32, width=1000)
        frame.pack_propagate(0)
        frame.pack()

        ut1 = us.UtilitieSparc("India","")
        paesi = ut1.lista_admin0()
        self.box_value_adm0 = StringVar()
        self.box_adm0 = ttk.Combobox(frame, textvariable = self.box_value_adm0)
        self.box_adm0['values'] = paesi
        self.box_adm0.current(36)
        self.box_adm0.pack(side=LEFT)

        self.emdat = Button(frame, text="EM-DAT Data",  fg="red",command=self.emdat)
        self.emdat.pack(side=LEFT)
        self.button = Button(frame, text="National Assessment", fg="red", command=self.national_calc).pack(side=LEFT)
        self.box_value_adm2 = StringVar()
        self.box_adm2 = ttk.Combobox(frame, textvariable = self.box_value_adm2)
        self.box_adm2['values'] = ' '
        self.box_adm2.pack(side=LEFT)

        self.sub_select = Button(frame, text="Fetch Admin", fg="blue",command=self.sub_select)
        self.sub_select.pack(side=LEFT)
        self.create_structure = Button(frame,text="Create Project",fg="blue", command = self.create_project)
        self.create_structure.pack(side=LEFT)
        self.button = Button(frame, text="Annual Hazard", fg="blue", command=self.hazard_assessment).pack(side=LEFT)
        self.button = Button(frame, text="Monthly Probability", fg="blue", command=self.monthly_distribution).pack(side=LEFT)
        self.button = Button(frame, text="Vulnerability", fg="blue", command=frame.quit).pack(side=LEFT)
        self.button = Button(frame, text="Next Step", fg="blue", command=frame.quit).pack(side=LEFT)

        root = Tk()
        root.title("SPARC Console")
        self.area_messaggi = Text(root, height=15, width=60, background="black", foreground="green")
        self.area_messaggi.pack()

    def sub_select(self):

        self.box_adm2.set(" ")
        paese_scelto = self.box_value_adm0.get()
        ut2 = us.UtilitieSparc(paese_scelto, "")
        global paesi_ritornati
        paesi_ritornati = ut2.lista_admin2(paese_scelto)
        self.box_adm2['values'] = sorted(paesi_ritornati[0])

    def emdat(self):

        paese = self.box_value_adm0.get()
        nuova_geocodifica = us.GeocodingEmDat(paese)
        if nuova_geocodifica.geolocate_accidents() == "Geocoded already!!":
            self.area_messaggi.insert(INSERT, "Geocoded already!!\n")
            nuova_geocodifica.plot_mappa()
        else:
            nuova_geocodifica.create_validated_coords()
            self.area_messaggi.insert(INSERT, "Geocoding Terminated\n")
            nuova_geocodifica.creazione_file_shp()
            self.area_messaggi.insert(INSERT, "Shapefile Created\n")
            nuova_geocodifica.create_heat_map()
            self.area_messaggi.insert(INSERT, "HeatMap Created\n")

    def create_project(self):

        paese = self.box_value_adm0.get()
        admin = self.box_value_adm2.get()

        for chiave_area in paesi_ritornati[1].iteritems():
            if chiave_area[1]['name_orig'] == admin:
               iso_global = chiave_area[0]
               global admin_global
               admin_global = chiave_area[1]['name_clean']
               self.area_messaggi.insert(INSERT, "Area ISOcode " + str(iso_global) + " modified name " + admin_global + "\n")
        ut3 = us.UtilitieSparc(paese, admin_global)
        print admin_global
        self.area_messaggi.insert(INSERT, ut3.creazione_struttura(admin_global))

    def hazard_assessment(self):

        paese = self.box_value_adm0.get()

        global newHazardAssessment
        newHazardAssessment = ha.HazardAssessment(paese, admin_global)
        self.area_messaggi.insert(INSERT, newHazardAssessment.estrazione_poly_admin())
        self.area_messaggi.insert(INSERT, newHazardAssessment.conversione_vettore_raster_admin())
        if newHazardAssessment.taglio_raster_popolazione()== "sipop":
            self.area_messaggi.insert(INSERT, "Population clipped....")
        elif newHazardAssessment.taglio_raster_popolazione()== "nopop":
            self.area_messaggi.insert(INSERT, "Population raster not yet released....")
            sys.exit()
        self.area_messaggi.insert(INSERT, newHazardAssessment.taglio_raster_inondazione_aggregato())
        self.area_messaggi.insert(INSERT, newHazardAssessment.taglio_raster_inondazione())
        self.area_messaggi.insert(INSERT, newHazardAssessment.calcolo_statistiche_zone_indondazione())
        newHazardAssessment.plot_affected()
        newHazardAssessment.plot_risk_curve()
        #newHazardAssessment.plot_risk_interpolation()
        newHazardAssessment.interpolazione_tempi_ritorno_intermedi()
        newHazardAssessment.gira_dati()
        newHazardAssessment.plot_risk_interpolation_linear()

    def monthly_distribution(self):

        paese = self.box_value_adm0.get()

        global newMontlhyDistribution
        newMontlhyDistribution = monDist.MonthlyDistribution(paese,admin_global)
        #self.area_messaggi.insert(INSERT,newMontlhyDistribution.cut_monthly_rasters())
        self.area_messaggi.insert(INSERT,newMontlhyDistribution.valore_precipitation_centroid())
        self.area_messaggi.insert(INSERT,newMontlhyDistribution.analisi_valori_da_normalizzare())
        self.area_messaggi.insert(INSERT,newMontlhyDistribution.historical_analysis_damages())
        newMontlhyDistribution.plot_monthly_danni()
        self.area_messaggi.insert(INSERT,newMontlhyDistribution.population_flood_prone_areas())
        self.area_messaggi.insert(INSERT, newMontlhyDistribution.calcolo_finale())
        newMontlhyDistribution.plottalo_bello()

    def national_calc(self):

        paese = self.box_value_adm0.get()

        import CountryCalculationsFlood
        CountryCalculationsFlood.data_processing_module_flood(paese)
        CountryCalculationsFlood.data_upload_module_flood(paese)

root = Tk()
root.title("SPARC Flood Assessment")
app = AppSPARC(root)
root.mainloop()



