#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

from Tkinter import *
import ttk

import pandas as pd
import pycountry

from intermedi.interfaces_discontinued import CompleteProcessingEMDAT as completeEMDAT


class AppSPARC_EMDAT:

    def __init__(self, master):

        self.OBJ_DB = completeEMDAT.ManagePostgresDBEMDAT('geonode', 'geonode')

        frame = Frame(master, height=32, width=400)
        frame.pack_propagate(0)
        frame.pack()

        self.collect_codes_country_level()
        self.box_value_adm0 = StringVar()
        self.box_adm0 = ttk.Combobox(frame, textvariable = self.box_value_adm0)
        self.box_adm0['values'] = self.lista_paesi
        self.box_adm0.current(0)
        self.box_adm0.pack(side=LEFT)

        self.box_value_hazard = StringVar()
        self.box_hazard = ttk.Combobox(frame, textvariable = self.box_value_hazard)
        self.box_hazard['values'] = ['Drought','Flood','Storm']
        self.box_hazard.current(1)
        self.box_hazard.pack(side=LEFT)

        self.button = Button(frame, text="Geocode EMDAT", fg="blue", command=self.national_emdata_geocoding).pack(side=LEFT)

        root = Tk()
        root.title("SPARC Console")
        self.area_messaggi = Text(root, height=15, width=60, background="black", foreground="green")
        self.area_messaggi.pack()

    def collect_codes_country_level(self):

        self.lista_paesi = self.OBJ_DB.all_country_db()

    def national_emdata_geocoding(self):

        paese = self.box_value_adm0.get()
        iso_paese =  pycountry.countries.get(name=paese).alpha3
        area =  self.OBJ_DB.select_ancillary_data_country(paese)

        #hazard = "Drought"
        hazard = self.box_hazard.get()

        OBJ_EMDAT = completeEMDAT.ScrapingEMDAT(area, iso_paese, hazard,paese)
        richiesta_paese = OBJ_EMDAT.scrape_EMDAT()
        danni_paese = richiesta_paese['data']
        df_danni = pd.DataFrame(danni_paese)
        df_danni = df_danni.set_index('disaster_no')
        OBJ_EMDAT.write_in_db(df_danni)
        df_paese = OBJ_EMDAT.read_from_db(hazard)

        lista_codici = list(df_paese.index.values)
        lista_locazioni = list(df_paese.location)

        #for codice in lista_codici:
        #    print codice
        lista_da_geocodificare = []
        #for codice, locazione in lista_locazioni:
        for codice, locazione in zip(df_paese.index.values,df_paese.location):
            if locazione is not None:
               loca_splittate = locazione.split(',')
               for loca in loca_splittate:
                   loca_clean = loca.strip()
                   print codice, loca_clean
                   lista_da_geocodificare.append(loca_clean)

        # OBJ_NOMINATIM = completeEMDAT.GeocodeEMDAT(paese, hazard)
        # OBJ_NOMINATIM.geolocate_accidents(lista_da_geocodificare, hazard)
        # quanti_dentro = OBJ_NOMINATIM.calc_poligono_controllo()
        # trovati_alcuni_dentro = quanti_dentro[0]
        # print "Dentro ci sono %d eventi" % trovati_alcuni_dentro
        # if trovati_alcuni_dentro > 0:
        #     OBJ_GISFILE = completeEMDAT.CreateGeocodedShp(paese, hazard)
        #     OBJ_GISFILE.creazione_file_shp()
        # self.area_messaggi.insert(INSERT, "Data for " + paese + " Uploaded in DB")
        #
        # OBJ_DB = completeEMDAT.ManagePostgresDBEMDAT


root = Tk()
root.title("SPARC EMDAT Analyzer")
app = AppSPARC_EMDAT(root)
root.mainloop()



