#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

from Tkinter import *
import ttk
import tkFileDialog
import os

import GDELT_Analysis
import GDELT_DB

obj_db = GDELT_DB.DB()
connessione = obj_db.db_connect()
paesi = obj_db.gather_paesi(connessione)
paese = ""
bbox = obj_db.boundinbox_paese(connessione,)

class AppSPARConflicts:

    def __init__(self, master):


        frame = Frame(master,height=32, width=600)
        frame.pack_propagate(0)
        frame.pack()

        self.select_file = Button(frame, text="Get File",  fg="red", command = self.open_file_chooser)
        self.select_file.pack(side=LEFT)

        self.box_value_country = StringVar()
        self.box_country = ttk.Combobox(frame, textvariable = [])
        self.box_country['values'] = paesi
        self.box_country.pack(side=LEFT)

        self.box_value_minYear = StringVar()
        self.box_minYear = ttk.Combobox(frame, textvariable = [])
        self.box_minYear['values'] = ['2010', '2011','2012','2013','2014','2015']
        self.box_minYear.pack(side=LEFT)

        self.box_value_maxYear = StringVar()
        self.box_maxYear = ttk.Combobox(frame, textvariable = [])
        self.box_maxYear['values'] = ['2010', '2011','2012','2013','2014','2015']
        self.box_maxYear.pack(side=LEFT)

        self.calcolo = Button(frame, text="Start Analysis", fg="red", command = self.subset_data)
        self.calcolo.pack(side=LEFT)

        self.area_messaggi = Text(root, height=15, width=70, background="black", foreground="green")
        self.area_messaggi.pack()

    def open_file_chooser(self):

        global nomeFile
        nomeFile = tkFileDialog.askopenfilename(parent=root, title='Choose GDELT archive file')
        if nomeFile != None:
            self.area_messaggi.insert(INSERT, nomeFile + "\n")
            dimensione_file = os.path.getsize(nomeFile)
            self.area_messaggi.insert(INSERT, " %s bytes in this file \n" % str(dimensione_file))

    def get_fields(self):

        col_names = GDELT_Analysis.GDELT_fields(nomeFile)
        for i, col_name in enumerate(col_names):
             self.area_messaggi.insert(INSERT, col_name + "\n")

    def get_iso(self,paese_ricerca):

        import psycopg2
        from psycopg2.extras import RealDictCursor

        schema = 'public'
        dbname = 'geonode-imports'
        user = 'geonode'
        password = 'geonode'
        connection_string = "dbname=%s user=%s password=%s" % (dbname, user, password)

        db_connessione = psycopg2.connect(connection_string)
        db_connessione.cursor_factory = RealDictCursor
        db_cursore = db_connessione.cursor()

        sql = "SELECT name,iso2,iso3 FROM sparc_wfp_countries WHERE name = '" + paese_ricerca + "';"
        db_cursore.execute(sql);
        risultati = db_cursore.fetchall()

        return risultati[0]['iso3']

    def subset_data(self):

        paese = self.box_country.get()
        iso = self.get_iso(paese)
        anno_min = self.box_minYear.get()
        anno_max = self.box_maxYear.get()
        messaggio = "%s con valore ISO %s between %s and %s \n" % (paese,iso, anno_min, anno_max)
        self.area_messaggi.insert(INSERT, messaggio)

        store_eventi = GDELT_Analysis.GDELT_subsetting(nomeFile,iso,anno_min,anno_max)
        quanti_eventi = "There are %d cases %s-related records between %s and %s. " % (len(store_eventi), paese, anno_min, anno_max)
        self.area_messaggi.insert(INSERT, quanti_eventi + "\n")

        coordinate = GDELT_Analysis.GDELT_coords(store_eventi)
        statistiche = GDELT_Analysis.GDELTS_stat(coordinate)
        self.area_messaggi.insert(INSERT, statistiche + "\n")
        GDELT_Analysis.GDELT_maplot(coordinate)

root = Tk()
root.title("SPARC Conflict Analysis")
app = AppSPARConflicts(root)
root.mainloop()




