#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

from Tkinter import *
import ttk
import tkFileDialog
import os
import datetime

import GDELT_Fetch
import GDELT_Analysis
import GDELT_DB

host = 'localhost'
schema = 'public'
dbname = 'geonode-imports'
user = 'geonode'
password = 'geonode'

oggetto_fetch = GDELT_Fetch.GDELT_Fetch()
oggetto_analysis = GDELT_Analysis.GDELT_Analysis()
oggetto_db = GDELT_DB.GDELT_DB(host, schema, dbname, user, password)
connessione = oggetto_db.apri_connessione()
paesi = oggetto_db.gather_paesi()

class AppSPARConflicts:

    def __init__(self, master):

        frame = Frame(master,height=32, width=875)
        frame.pack_propagate(0)
        frame.pack()

        self.box_value_country = StringVar()
        self.box_country = ttk.Combobox(frame, textvariable = [])
        self.box_country['values'] = sorted(paesi)
        self.box_country.pack(side=LEFT)

        self.box_value_minYear = StringVar()
        self.box_minYear = ttk.Combobox(frame, textvariable= [])
        self.box_minYear['values'] = ['2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013']
        self.box_minYear.pack(side=LEFT)

        self.box_value_maxYear = StringVar()
        self.box_maxYear = ttk.Combobox(frame, textvariable = [])
        self.box_maxYear['values'] = ['2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013']
        self.box_maxYear.pack(side=LEFT)

        #self.iso_bbox = Button(frame, text="ISO BBOX FIPS", fg="blue", command = self.get_iso_bbox)
        #self.iso_bbox.pack(side=LEFT)

        # self.select_file = Button(frame, text="Weekly Trend",  fg="darkgreen", command = self.weekly_trend)
        # self.select_file.pack(side=LEFT)

        self.select_file = Button(frame, text="Current Analysis (2014/2015)", fg="blue", command = self.GDELT_current)
        self.select_file.pack(side=LEFT)

        self.select_file = Button(frame, text="Load Historical File",  fg="red", command = self.open_file_chooser)
        self.select_file.pack(side=LEFT)

        self.calcolo = Button(frame, text="Historical Analysis (1973/2013)", fg="red", command = self.GDELT_historical)
        self.calcolo.pack(side=LEFT)

        self.scrollbar = Scrollbar(root)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.area_messaggi = Text(root, height=15, width=105, background="black", foreground="green")
        self.area_messaggi.pack()

        # attach listbox to scrollbar
        self.area_messaggi.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.area_messaggi.yview)

    def get_iso_bbox(self):

        paese_ricerca = self.box_country.get()
        print oggetto_db.country_codes(paese_ricerca)[0]
        fips = oggetto_db.country_codes(paese_ricerca)[0][3]
        iso3 = oggetto_db.country_codes(paese_ricerca)[0][2]
        bbox = oggetto_db.boundinbox_paese(paese_ricerca)
        self.area_messaggi.insert(INSERT, str(iso3) + str(bbox) + str(fips) + "\n")

        return bbox, iso3, fips

    def weekly_trend(self):

        now = datetime.datetime.now()
        meno_7 = datetime.timedelta(days=7)
        mese_passato = now - meno_7
        massimo = now.strftime("%Y%m%d")
        minimo = mese_passato.strftime("%Y%m%d")
        self.area_messaggi.insert(INSERT,"Between %s and %s" % (str(massimo), str(minimo)))

        fips = self.get_iso_bbox()[2]
        lista_files = oggetto_fetch.gdelt_connect(minimo, massimo)
        self.area_messaggi.insert(INSERT, "Found %d files\n" % len(lista_files))

        esito = oggetto_fetch.gdelt_fetch(lista_files, fips)
        self.area_messaggi.insert(INSERT, esito)

        weekly_df = oggetto_fetch.gdelt_pandas_conversion(fips)

        self.area_messaggi.insert(INSERT, weekly_df)

    def GDELT_current(self):

        anno_inizio = '2014'
        now = datetime.datetime.now()
        anno_fine = now.year

        self.area_messaggi.insert(INSERT,"Between %s and %s \n" % (str(anno_inizio), str(anno_fine)))

        fips = self.get_iso_bbox()[2]
        lista_files = oggetto_fetch.gdelt_connect(anno_inizio, anno_fine)
        self.area_messaggi.insert(INSERT, "Found %d files\n" % len(lista_files))
        self.area_messaggi.insert(INSERT, "Ultimo file %s primo file %s \n" % (lista_files[0],lista_files[-1]))

        esito = oggetto_fetch.gdelt_fetch(lista_files, fips)
        self.area_messaggi.insert(INSERT, esito)

        montly_df = oggetto_fetch.gdelt_pandas_conversion(fips)

    def open_file_chooser(self):

        global nomeFile
        nomeFile = tkFileDialog.askopenfilename(parent=root, title='Choose GDELT archive file')
        print nomeFile

        if nomeFile != None:
            self.area_messaggi.insert(INSERT, nomeFile + "\n")
            dimensione_file = os.path.getsize(nomeFile)
            self.area_messaggi.insert(INSERT, " %s bytes in this file \n" % str(dimensione_file))

    def get_fields(self):

        col_names = oggetto_analysis.GDELT_fields(nomeFile)
        for i, col_name in enumerate(col_names):
             self.area_messaggi.insert(INSERT, col_name + "\n")

    def GDELT_historical(self):

        paese = self.box_country.get()
        bbox, iso, fips = self.get_iso_bbox()
        anno_min = self.box_minYear.get()
        anno_max = self.box_maxYear.get()
        messaggio = "%s ISO %s between %s and %s \n" % (paese, iso, anno_min, anno_max)
        self.area_messaggi.insert(INSERT, messaggio)

        store_eventi = oggetto_analysis.GDELT_subsetting(nomeFile, iso, anno_min, anno_max)

        import pandas as pd

        local_path = 'C:/data/tools/sparc/conflicts/SPARC_GDELT/test_data/results/'
        DF = pd.DataFrame(store_eventi)
        DF.to_pickle(local_path + paese + '.pickle')

        oggetto_db.depickle_pandas_historical(paese)

        quanti_eventi = "There are %d cases %s-related records between %s and %s. " % (len(store_eventi), paese, anno_min, anno_max)
        self.area_messaggi.insert(INSERT, quanti_eventi + "\n")

        coordinate = oggetto_analysis.GDELT_coords(store_eventi)[0]

        #statistiche = oggetto_gdelt.GDELTS_stat(coordinate)
        #self.area_messaggi.insert(INSERT, statistiche + "\n")

        oggetto_analysis.GDELT_maplot(coordinate, bbox[0], bbox[1], bbox[3], bbox[2], bbox[5], bbox[4])

root = Tk()
root.title("SPARC Conflict Analysis")
app = AppSPARConflicts(root)
root.mainloop()




