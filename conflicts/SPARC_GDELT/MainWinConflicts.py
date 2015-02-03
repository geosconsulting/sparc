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

oggetto_url_gdelt = GDELT_Fetch.GDELT_Fetch()
oggetto_gdelt = GDELT_Analysis.GDELT_Analysis()
oggetto_db = GDELT_DB.DB()
connessione = oggetto_db.db_connect()
paesi = oggetto_db.gather_paesi(connessione)

class AppSPARConflicts:

    def __init__(self, master):

        frame = Frame(master,height=32, width=820)
        frame.pack_propagate(0)
        frame.pack()

        self.box_value_country = StringVar()
        self.box_country = ttk.Combobox(frame, textvariable = [])
        self.box_country['values'] = sorted(paesi)
        self.box_country.pack(side=LEFT)

        self.box_value_minYear = StringVar()
        self.box_minYear = ttk.Combobox(frame, textvariable= [])
        self.box_minYear['values'] = ['2010', '2011', '2012', '2013', '2014', '2015']
        self.box_minYear.pack(side=LEFT)

        self.box_value_maxYear = StringVar()
        self.box_maxYear = ttk.Combobox(frame, textvariable = [])
        self.box_maxYear['values'] = ['2010', '2011', '2012', '2013', '2014', '2015']
        self.box_maxYear.pack(side=LEFT)

        #self.iso_bbox = Button(frame, text="ISO BBOX FIPS", fg="blue", command = self.get_iso_bbox)
        #self.iso_bbox.pack(side=LEFT)

        self.select_file = Button(frame, text="Weekly Trend",  fg="darkgreen", command = self.weekly_trend)
        self.select_file.pack(side=LEFT)

        self.select_file = Button(frame, text="Monthly Trend",  fg="darkgreen", command = self.monthly_trend)
        self.select_file.pack(side=LEFT)

        self.select_file = Button(frame, text="Historical Records",  fg="red", command = self.open_file_chooser)
        self.select_file.pack(side=LEFT)

        self.calcolo = Button(frame, text="Start Analysis", fg="red", command = self.subset_data)
        self.calcolo.pack(side=LEFT)

        self.area_messaggi = Text(root, height=15, width=100, background="black", foreground="green")
        self.area_messaggi.pack()

    def get_iso_bbox(self):

        paese_ricerca = self.box_country.get()
        fips = oggetto_db.codici_admin(connessione,paese_ricerca)[0]['fips']
        iso3 = oggetto_db.codici_admin(connessione,paese_ricerca)[0]['iso3']
        bbox = oggetto_db.boundinbox_paese(connessione, paese_ricerca)
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
        lista_files = oggetto_url_gdelt.gdelt_connect(minimo, massimo)
        self.area_messaggi.insert(INSERT, "Found %d files\n" % len(lista_files))

        esito = oggetto_url_gdelt.gdelt_country(lista_files, fips)
        self.area_messaggi.insert(INSERT, esito)

        weekly_df = oggetto_url_gdelt.gdelt_pandas_conversion(fips)

    def monthly_trend(self):

        now = datetime.datetime.now()
        meno_30 = datetime.timedelta(days=30)
        mese_passato = now - meno_30
        # giorno = now.day
        # mese = now.month
        # anno = now.year
        massimo = now.strftime("%Y%m%d")
        minimo = mese_passato.strftime("%Y%m%d")
        self.area_messaggi.insert(INSERT,"Between %s and %s" % (str(massimo), str(minimo)))

        fips = self.get_iso_bbox()[2]
        # anno_min = self.box_minYear.get()
        # anno_max = self.box_maxYear.get()
        lista_files = oggetto_url_gdelt.gdelt_connect(minimo, massimo)
        self.area_messaggi.insert(INSERT, "Found %d files\n" % len(lista_files))

        esito = oggetto_url_gdelt.gdelt_country(lista_files, fips)
        self.area_messaggi.insert(INSERT, esito)

        montly_df = oggetto_url_gdelt.gdelt_pandas_conversion(fips)

    def open_file_chooser(self):

        global nomeFile
        nomeFile = tkFileDialog.askopenfilename(parent=root, title='Choose GDELT archive file')
        if nomeFile != None:
            self.area_messaggi.insert(INSERT, nomeFile + "\n")
            dimensione_file = os.path.getsize(nomeFile)
            self.area_messaggi.insert(INSERT, " %s bytes in this file \n" % str(dimensione_file))

    def get_fields(self):

        col_names = oggetto_gdelt.GDELT_fields(nomeFile)
        for i, col_name in enumerate(col_names):
             self.area_messaggi.insert(INSERT, col_name + "\n")

    def subset_data(self):

        paese = self.box_country.get()
        bbox, iso, fips = self.get_iso_bbox()
        anno_min = self.box_minYear.get()
        anno_max = self.box_maxYear.get()
        messaggio = "%s ISO %s between %s and %s \n" % (paese, iso, anno_min, anno_max)
        self.area_messaggi.insert(INSERT, messaggio)

        store_eventi = oggetto_gdelt.GDELT_subsetting(nomeFile, iso, anno_min, anno_max)
        quanti_eventi = "There are %d cases %s-related records between %s and %s. " % (len(store_eventi), paese, anno_min, anno_max)
        self.area_messaggi.insert(INSERT, quanti_eventi + "\n")

        coordinate = oggetto_gdelt.GDELT_coords(store_eventi)[0]

        #statistiche = oggetto_gdelt.GDELTS_stat(coordinate)
        #self.area_messaggi.insert(INSERT, statistiche + "\n")

        oggetto_gdelt.GDELT_maplot(coordinate, bbox[0], bbox[1], bbox[3], bbox[2], bbox[5], bbox[4])

root = Tk()
root.title("SPARC Conflict Analysis")
app = AppSPARConflicts(root)
root.mainloop()




