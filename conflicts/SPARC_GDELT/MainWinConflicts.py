#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

from Tkinter import *
import ttk
import tkFileDialog
import os
import datetime

import GDELT_Processor
import GDELT_Analysis
import GDELT_DB

host = 'localhost'
schema = 'public'
dbname = 'geonode-imports'
user = 'geonode'
password = 'geonode'

oggetto_data_processor = GDELT_Processor.GDELT_Fetch()
oggetto_data_analysis = GDELT_Analysis.GDELT_Analysis()
oggetto_db = GDELT_DB.GDELT_DB(host, schema, dbname, user, password)
connessione = oggetto_db.apri_connessione()
paesi = oggetto_db.gather_paesi()

class AppSPARConflicts:

    def __init__(self, finestraConflicts):

        finestraConflicts.geometry("470x325+30+30")
        self.now = datetime.datetime.now()

        #Scelta Paese Combobox
        self.box_value_country = StringVar()
        self.box_country = ttk.Combobox(finestraConflicts, textvariable = [])
        self.box_country['values'] = sorted(paesi)
        self.box_country.current(0)
        self.box_country.place(x = 0 , y = 2, width=250, height=25)

        #Area Messaggi
        self.area_messaggi = Text(root, height=15, width=85, background="black", foreground="green")
        self.area_messaggi.place(x= 0, y=30, width=250, height= 290)
        self.scr = Scrollbar(finestraConflicts, command = self.area_messaggi.yview)
        self.scr.place(x=240, y= 30, width=10, height=290)
        self.area_messaggi.config(yscrollcommand=self.scr.set)

        #SEZIONE ANALiSI DATI STORICI FINO 2000
        frame_historical = LabelFrame(finestraConflicts, text= "Historical Analysis (1979/2013)", bg="burlywood", relief = SUNKEN,border = 1)
        frame_historical.place(x = 260, y = 5, width=290, height=130)

        self.select_file = Button(finestraConflicts, text="Load Historical File",  fg="red", command = self.open_file_chooser)
        self.select_file.place(x = 270, y = 25)

        lista_anni_storici = list(range(1973,2013))
        #Scelta anni minimo massimo per analisi storica
        anni = Label(finestraConflicts, text="Minimum/Maximum Years",fg="red",bg="burlywood")
        anni.place(x = 270, y = 50, width=166)
        self.box_value_minYear = StringVar()
        self.box_minYear = ttk.Combobox(finestraConflicts, textvariable= [], width=7)
        self.box_minYear['values'] = lista_anni_storici
        self.box_minYear.place(x = 270, y = 70, width=80)

        self.box_value_maxYear = StringVar()
        self.box_maxYear = ttk.Combobox(finestraConflicts, textvariable = [],width=7)
        self.box_maxYear['values'] = lista_anni_storici
        self.box_maxYear.place(x = 355, y= 70, width=80)

        self.calcolo_storico = Button(finestraConflicts, text="Start Analysis", fg="red", command = self.GDELT_historical)
        self.calcolo_storico.place(x = 270, y= 100, width=120)

        #self.iso_bbox = Button(finestraConflicts, text="ISO BBOX FIPS", fg="blue", command = self.get_iso_bbox)
        #self.iso_bbox.pack(side=LEFT)

        #SEZIONE ANALiSI DATI CORRENTI DAL 2000
        in_che_anno_siamo = self.now.year
        frame_current = LabelFrame(finestraConflicts, text= "Recent Events Analysis",
                                   fg="white", bg="darkgreen", relief = SUNKEN, border = 1)
        frame_current.place(x = 260, y = 140, width=200, height=180)

        self.analisi_settimanale = Button(finestraConflicts, text="Weekly Trend",  fg="darkgreen", command = self.weekly_trend)
        self.analisi_settimanale.place(x = 265, y = 160, width=90)

        self.analisi_mensile = Button(finestraConflicts, text="Monthly Trend",  fg="darkgreen", command = self.monthly_trend)
        self.analisi_mensile.place(x = 360, y = 160, width=90)

        self.analisi_settimanale = Button(finestraConflicts, text="Quarterly",  fg="darkgreen", command = self.quarterly_trend)
        self.analisi_settimanale.place(x = 265, y = 190, width=90)

        self.analisi_mensile = Button(finestraConflicts, text="Semestral",  fg="darkgreen", command = self.semestral_trend)
        self.analisi_mensile.place(x = 360, y = 190, width=90)

        #Scelta anni minimo massimo per analisi corrente
        lista_anni_correnti = list(range(2013,in_che_anno_siamo+1))
        anni_current = Label(finestraConflicts, text="Minimum/Maximum Years",fg="white",bg="darkgreen")
        anni_current.place(x = 270, y = 220, width=166)

        self.box_value_minYear_current = StringVar()
        self.box_minYear_current = ttk.Combobox(finestraConflicts, textvariable= [], width=7)
        self.box_minYear_current['values'] = lista_anni_correnti
        self.box_minYear_current.place(x = 270, y = 245, width=80)

        self.box_value_maxYear_current = StringVar()
        self.box_maxYear_current = ttk.Combobox(finestraConflicts, textvariable = [],width=7)
        self.box_maxYear_current['values'] = lista_anni_correnti
        self.box_maxYear_current.place(x = 355, y= 245, width=80)

        self.analisi_corrente = Button(finestraConflicts, text="Start Analysis", fg="darkgreen", command = self.GDELT_current)
        self.analisi_corrente.place(x = 270, y= 280)

        finestraConflicts.mainloop()

    def get_iso_bbox(self):

        paese_ricerca = self.box_country.get()
        print oggetto_db.country_codes(paese_ricerca)[0]
        fips = oggetto_db.country_codes(paese_ricerca)[0][3]
        iso3 = oggetto_db.country_codes(paese_ricerca)[0][2]
        bbox = oggetto_db.boundinbox_paese(paese_ricerca)
        self.area_messaggi.insert(INSERT, str(iso3) + str(bbox) + str(fips) + "\n")

        return bbox, iso3, fips

    def weekly_trend(self):

        meno_7 = self.now - datetime.timedelta(days = 7)
        print self.now, meno_7

        massimo = self.now.strftime("%Y%m%d")
        minimo = meno_7.strftime("%Y%m%d")
        print massimo,minimo
        self.area_messaggi.insert(INSERT,"Between %s and %s" % (str(massimo), str(minimo)))

        fips = self.get_iso_bbox()[2]
        self.area_messaggi.insert(INSERT,"FIPS %s" % (str(fips)))
        lista_files = oggetto_data_processor.collect_file_list(minimo, massimo)
        self.area_messaggi.insert(INSERT, "%d files\n" % len(lista_files))

        esito = oggetto_data_processor.download_process_delete(lista_files, fips)
        self.area_messaggi.insert(INSERT, esito)

        paese_weekly = self.box_country.get()
        oggetto_data_processor.gdelt_pandas_conversion(fips, paese_weekly, 'weekly')
        df = oggetto_data_analysis.depickle_current("weekly", paese_weekly)
        oggetto_data_analysis.chart_country(df)

    def monthly_trend(self):

        meno_30 = self.now - datetime.timedelta(days = 30)
        print self.now, meno_30

        massimo = self.now.strftime("%Y%m%d")
        minimo = meno_30.strftime("%Y%m%d")
        print massimo,minimo
        self.area_messaggi.insert(INSERT,"Between %s and %s" % (str(massimo), str(minimo)))

        fips = self.get_iso_bbox()[2]
        self.area_messaggi.insert(INSERT,"FIPS %s" % (str(fips)))

        lista_files = oggetto_data_processor.collect_file_list(minimo, massimo)
        self.area_messaggi.insert(INSERT, "%d files\n" % len(lista_files))

        esito = oggetto_data_processor.download_process_delete(lista_files, fips)
        self.area_messaggi.insert(INSERT, esito)

        paese_montlhy = self.box_country.get()
        oggetto_data_processor.gdelt_pandas_conversion(fips,paese_montlhy,'monthly')
        df = oggetto_data_analysis.depickle_current("monthly", paese_montlhy)
        oggetto_data_analysis.chart_country(df)

    def quarterly_trend(self):

        meno_90 = self.now - datetime.timedelta(days = 90)
        print self.now, meno_90

        massimo = self.now.strftime("%Y%m%d")
        minimo = meno_90.strftime("%Y%m%d")
        print massimo,minimo
        self.area_messaggi.insert(INSERT,"Between %s and %s" % (str(massimo), str(minimo)))

        fips = self.get_iso_bbox()[2]
        self.area_messaggi.insert(INSERT,"FIPS %s" % (str(fips)))

        lista_files = oggetto_data_processor.collect_file_list(minimo, massimo)
        self.area_messaggi.insert(INSERT, "%d files\n" % len(lista_files))

        esito = oggetto_data_processor.download_process_delete(lista_files, fips)
        self.area_messaggi.insert(INSERT, esito)

        paese_quarterly = self.box_country.get()
        oggetto_data_processor.gdelt_pandas_conversion(fips,paese_quarterly, 'quarterly')

        df = oggetto_data_analysis.depickle_current("quarterly", paese_quarterly)
        oggetto_data_analysis.chart_country(df)

    def semestral_trend(self):

        meno_180 = self.now - datetime.timedelta(days = 180)
        print self.now, meno_180

        massimo = self.now.strftime("%Y%m%d")
        minimo = meno_180.strftime("%Y%m%d")
        print massimo,minimo
        self.area_messaggi.insert(INSERT,"Between %s and %s" % (str(massimo), str(minimo)))

        fips = self.get_iso_bbox()[2]
        self.area_messaggi.insert(INSERT,"FIPS %s" % (str(fips)))

        lista_files = oggetto_data_processor.collect_file_list(minimo, massimo)
        self.area_messaggi.insert(INSERT, "%d files\n" % len(lista_files))

        esito = oggetto_data_processor.download_process_delete(lista_files, fips)
        self.area_messaggi.insert(INSERT, esito)

        paese_semestral = self.box_country.get()
        oggetto_data_processor.gdelt_pandas_conversion(fips,paese_semestral,'semestral')

        df = oggetto_data_analysis.depickle_current("semestral", paese_semestral)
        oggetto_data_analysis.chart_country(df)

    def GDELT_current(self):

        anno_inizio = '2014'
        now = datetime.datetime.now()
        anno_fine = now.year

        self.area_messaggi.insert(INSERT,"Between %s and %s \n" % (str(anno_inizio), str(anno_fine)))

        fips = self.get_iso_bbox()[2]
        lista_files = oggetto_data_processor.gdelt_connect(anno_inizio, anno_fine)
        self.area_messaggi.insert(INSERT, "Found %d files\n" % len(lista_files))
        self.area_messaggi.insert(INSERT, "Ultimo file %s primo file %s \n" % (lista_files[0],lista_files[-1]))

        esito = oggetto_data_processor.download_process_delete(lista_files, fips)
        self.area_messaggi.insert(INSERT, esito)

        montly_df = oggetto_data_processor.gdelt_pandas_conversion(fips,self.paese,'annual')

    def open_file_chooser(self):

        global nomeFile
        nomeFile = tkFileDialog.askopenfilename(parent=root, title='Choose GDELT archive file')
        print len(nomeFile)

        if nomeFile != None and len(nomeFile)>0:
            self.area_messaggi.insert(INSERT, nomeFile + "\n")
            dimensione_file = os.path.getsize(nomeFile)
            self.area_messaggi.insert(INSERT, " %s bytes in this file \n" % str(dimensione_file))
        else:
            pass

    def get_fields(self):

        col_names = oggetto_data_analysis.GDELT_fields(nomeFile)
        for i, col_name in enumerate(col_names):
             self.area_messaggi.insert(INSERT, col_name + "\n")

    def GDELT_historical(self):

        paese = self.box_country.get()
        bbox, iso, fips = self.get_iso_bbox()
        anno_min = self.box_minYear.get()
        anno_max = self.box_maxYear.get()
        messaggio = "%s ISO %s between %s and %s \n" % (paese, iso, anno_min, anno_max)
        self.area_messaggi.insert(INSERT, messaggio)

        store_eventi = oggetto_data_analysis.GDELT_subsetting(nomeFile, iso, anno_min, anno_max)

        import pandas as pd

        local_path = 'C:/data/tools/sparc/conflicts/SPARC_GDELT/test_data/results/'
        DF = pd.DataFrame(store_eventi)
        DF.to_pickle(local_path + paese + '.pickle')

        oggetto_db.depickle_pandas_historical(paese)

        quanti_eventi = "There are %d cases %s-related records between %s and %s. " % (len(store_eventi), paese, anno_min, anno_max)
        self.area_messaggi.insert(INSERT, quanti_eventi + "\n")

        coordinate = oggetto_data_analysis.GDELT_coords(store_eventi)[0]

        #statistiche = oggetto_gdelt.GDELTS_stat(coordinate)
        #self.area_messaggi.insert(INSERT, statistiche + "\n")

        oggetto_data_analysis.GDELT_maplot(coordinate, bbox[0], bbox[1], bbox[3], bbox[2], bbox[5], bbox[4])

root = Tk()
root.title("SPARC Conflict Analysis")
app = AppSPARConflicts(root)





