__author__ = 'fabio.lana'

import os
import glob
import csv
import numpy as np
import math
import matplotlib.pyplot as plt
import pylab

import arcpy
arcpy.CheckOutExtension("spatial")
from arcpy import env
env.overwriteOutput = "true"

class MonthlyDistribution(object):

    proj_dir = os.getcwd() + "/projects/"
    shape_countries = os.getcwd() + "/input_data/gaul/gaul_wfp.shp"
    pop_distr = os.getcwd() + "/input_data/population/popmap10.tif"
    flood_aggregated = os.getcwd() + "/input_data/flood/rp_aggregat.tif"
    historical_accidents_file = os.getcwd() + "/input_data/historical_data/floods - refine.csv"
    monthly_precipitation_dir = os.getcwd() + "/input_data/precipitation/"

    def __init__(self, paese, admin):

       self.paese = paese
       self.admin = admin
       self.dirOut = MonthlyDistribution.proj_dir + paese + "/" + admin + "/"

    def build_value_list(self,list_val):

        la_lista_finale = {}
        for key, val in list_val.iteritems():
            if key == 'prc01.tif':
                la_lista_finale[1] = val
            elif key == 'prc02.tif':
                la_lista_finale[2] = val
            elif key == 'prc03.tif':
                la_lista_finale[3] = val
            elif key == 'prc04.tif':
                la_lista_finale[4] = val
            elif key == 'prc05.tif':
                la_lista_finale[5] = val
            elif key == 'prc06.tif':
                la_lista_finale[6] = val
            elif key == 'prc07.tif':
                la_lista_finale[7] = val
            elif key == 'prc08.tif':
                la_lista_finale[8] = val
            elif key == 'prc09.tif':
                la_lista_finale[9] = val
            elif key == 'prc10.tif':
                la_lista_finale[10] = val
            elif key == 'prc11.tif':
                la_lista_finale[11] = val
            elif key == 'prc12.tif':
                la_lista_finale[12] = val

        for k, v in la_lista_finale.iteritems():
            if v is None:
                la_lista_finale[k] = 0

        return la_lista_finale

    def cut_monthly_rasters(self):

        os.chdir(self.monthly_precipitation_dir)
        lista_raster = glob.glob("*.tif")
        admin_rast = self.dirOut + self.admin + "_rst.tif"
        print admin_rast

        valori_mensili = {}
        for raster_mese in lista_raster:
            mese_raster = arcpy.Raster(self.monthly_precipitation_dir + raster_mese)
            mese_tagliato = arcpy.sa.ExtractByRectangle(mese_raster, admin_rast)
            nome = self.dirOut + self.admin + "_" + str(raster_mese)
            mese_tagliato.save(nome)
            valori_mensili[raster_mese] = mese_tagliato.mean

        global dizionario_in
        dizionario_in = self.build_value_list(valori_mensili)
        with open(self.dirOut + self.admin + "_prec.csv", 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for linea in dizionario_in.iteritems():
                csvwriter.writerow(linea)

        global ritornati_somma
        ritornati_somma = sum(dizionario_in.values())

        return "Monthly Probability Function calculated....\n"

    def valore_precipitation_centroid(self):

        file_amministrativo = self.dirOut + self.admin + ".shp"
        file_centroide = self.dirOut + self.admin + "_ctrd.shp"
        #print file_centroide
        adm2_centroid = arcpy.FeatureToPoint_management(file_amministrativo,file_centroide, "CENTROID")
        coords = arcpy.da.SearchCursor(adm2_centroid,["SHAPE@XY"])
        for polyg in coords:
            x,y = polyg[0]

        os.chdir(self.monthly_precipitation_dir)
        lista_raster = glob.glob("*.tif")

        valori_mensili = {}
        for raster_mese in lista_raster:
            result = arcpy.GetCellValue_management(raster_mese, str(x) + " " + str(y))
            valori_mensili[raster_mese] = int(result[0])

        #print valori_mensili

        global dizionario_in
        dizionario_in = self.build_value_list(valori_mensili)
        with open(self.dirOut + self.admin + "_prec.csv", 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for linea in dizionario_in.iteritems():
                csvwriter.writerow(linea)

        #print dizionario_in
        #global ritornati_somma
        #ritornati_somma = sum(dizionario_in.values())

        return "Monthly Probability Function calculated....\n"

    def analisi_valori_da_normalizzare(self):

        mese_di_minimo_valore = min(dizionario_in, key = dizionario_in.get)
        minimo_valore = dizionario_in[mese_di_minimo_valore]
        mese_di_massimo_valore = max(dizionario_in, key = dizionario_in.get)
        massimo_valore = dizionario_in[mese_di_massimo_valore]

        #NORMALIZZAZIONE FATTA A MANO CALCOLANDO TUTTO
        #LO USO PERCHE ALTRIMENTI SI INCASINA LA GENERAZIONE DEI PLOTS
        global normalizzati
        normalizzati = {}
        for linea in dizionario_in.iteritems():
            x_new = (linea[1] - float(minimo_valore))/(float(massimo_valore)-float(minimo_valore))
            normalizzati[linea[0]] = x_new

        with open(self.dirOut + self.admin + "_prec_norm.csv", 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for linea in normalizzati.iteritems():
                  csvwriter.writerow(linea)

        return "Monthly Probability Values normalized....\n"

    def historical_analysis_damages(self):

        import collections

        file_incidenti_in = open(self.historical_accidents_file)
        next(file_incidenti_in)
        mesi = []
        for linea in file_incidenti_in:
            splittato_comma = linea.split(",")
            if splittato_comma[2] == self.paese:
                if splittato_comma[0] == 0 or splittato_comma[1] == 0:
                    print splittato_comma[9]
                splittato_mese_inzio = splittato_comma[0].split("/")
                splittato_mese_fine = splittato_comma[1].split("/")
                #print splittato_mese_inzio[1], splittato_mese_fine[1]
                if splittato_mese_inzio[1]!=0 or splittato_mese_fine[0]!=0:
                    differenza = int(splittato_mese_fine[1]) - int(splittato_mese_inzio[1])
                    if differenza == 0:
                         mesi.append(int(splittato_mese_inzio[1]))
                    else:
                        mesi.append(int(splittato_mese_inzio[1]))
                        for illo in range(1, differenza+1):
                            mesi.append(int(splittato_mese_inzio[1]) + illo)
        file_incidenti_in.close()

        conta_mesi = collections.Counter(mesi)
        conta_mesi_ord = collections.OrderedDict(sorted(conta_mesi.items()))

        missing = []
        for indice in range(1, 13):
            if indice not in conta_mesi_ord:
                missing.append(indice)

        for valore in missing:
            conta_mesi_ord[valore] = 0

        global danni_mesi
        danni_mesi = collections.OrderedDict(sorted(conta_mesi_ord.items()))

        return "Monthly subdivision of incidents calculated....\n"

    def plot_monthly_danni(self):

        labella_y = "Precipitation"
        titolo = "EM-DAT Registered Incidents"
        fig = pylab.gcf()
        fig.canvas.set_window_title(titolo)
        plt.grid(True)

        # Plot y1 vs x in blue on the left vertical axis.
        plt.xlabel("Months")
        plt.ylabel("Historical Incidents related with Floods EM-DAT", color="b")
        plt.tick_params(axis="y", labelcolor="b")
        plt.bar(range(len(danni_mesi)), danni_mesi.values(), align='center', color='g')

        plt.twinx()
        plt.ylabel(labella_y, color="r")
        plt.tick_params(axis="y", labelcolor="r")
        plt.plot(range(len(dizionario_in)), dizionario_in.values(), 'r--')
        plt.xticks(range(len(dizionario_in)), dizionario_in.keys())

        plt.title(self.admin)
        plt.show()

    def population_flood_prone_areas(self):

        global population_in_flood_prone_areas
        tabella_calcolata = self.dirOut + self.admin + "_pop_stat.dbf"
        tab_cur_pop = arcpy.da.SearchCursor(tabella_calcolata, "*")
        campo_tempo_ritorno = tab_cur_pop.fields.index('Value')
        campo_pop_affected = tab_cur_pop.fields.index('SUM')
        population_in_flood_prone_areas = {}
        for riga_pop in tab_cur_pop:
            tempo_ritorno = riga_pop[campo_tempo_ritorno]
            population_tempo_ritorno = riga_pop[campo_pop_affected]
            if population_tempo_ritorno > 0:
                population_in_flood_prone_areas[tempo_ritorno] = population_tempo_ritorno

        return "Population in flood prone areas calculated....\n"

    def calcolo_finale(self):

        global persone_pesi
        persone_pesi = dict()
        persone_pesi['25'] = {}
        persone_pesi['50'] = {}
        persone_pesi['100'] = {}
        persone_pesi['200'] = {}
        persone_pesi['500'] = {}
        persone_pesi['1000'] = {}

        valori25 = []
        valori50 = []
        valori100 = []
        valori200 = []
        valori500 = []
        valori1000 = []

        iteratore = 0
        ildizio_chiavi = population_in_flood_prone_areas.keys()
        irps = [25, 50, 100, 200, 500, 1000]
        for chiave in irps:
            if chiave in ildizio_chiavi:
                pass
            else:
                population_in_flood_prone_areas[chiave] = 0

        for persone_chiave, persone_valore in sorted(population_in_flood_prone_areas.iteritems()):
            iteratore += 1
            for peso_chiave, peso_valore in normalizzati.iteritems():
                persone = persone_valore * peso_valore
                if persone_chiave == 25:
                    valori25.append(int(persone))
                    persone_pesi['25'][peso_chiave] = int(persone)
                elif persone_chiave == 50:
                    valori50.append(int(persone))
                    persone_pesi['50'][peso_chiave] = persone
                elif persone_chiave == 100:
                    valori100.append(int(persone))
                    persone_pesi['100'][peso_chiave] = persone
                elif persone_chiave == 200:
                    valori200.append(int(persone))
                    persone_pesi['200'][peso_chiave] = persone
                elif persone_chiave == 500:
                    valori500.append(int(persone))
                    persone_pesi['500'][peso_chiave] = persone
                elif persone_chiave == 1000:
                    valori1000.append(int(persone))
                    persone_pesi['1000'][peso_chiave-1] = persone

        return "Monthly people divided.....\n"

    def plottalo_bello(self):

        columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        rows = ['%d RP' % x for x in (1000, 500, 200, 100, 50, 25)]

        people_affected_rp = []
        for cada in persone_pesi.itervalues():
            myRoundedList = [round(elem, 2) for elem in cada.values()]
            people_affected_rp.append(myRoundedList)

        print people_affected_rp

        matrice = np.asarray(people_affected_rp)
        maximo_y = math.ceil(max(matrice.sum(0))/500)*500
        values = np.arange(0, maximo_y, 100000)
        value_increment = 1

        # Get some pastel shades for the colors
        colors = plt.cm.OrRd(np.linspace(0, 0.5, len(rows)))
        n_rows = len(persone_pesi)

        #index = np.arange(len(columns)) + 0.3
        index = np.arange(len(columns))
        bar_width = 1

        # Initialize the vertical-offset for the stacked bar chart.
        y_offset = np.array([0.0] * len(columns))

        # Plot bars and create text labels for the table
        cell_text = []
        for row in range(n_rows):
            plt.bar(index, people_affected_rp[row], bar_width, bottom=y_offset, color=colors[row])
            y_offset = y_offset + people_affected_rp[row]
            cell_text.append(['%d' % (x) for x in y_offset])
        # Reverse colors and text labels to display the last value at the top.
        colors = colors[::-1]
        cell_text.reverse()

        # Add a table at the bottom of the axes
        the_table = plt.table(cellText=cell_text,
                              rowLabels=rows,
                              rowColours=colors,
                              colLabels=columns,
                              loc ='bottom')

        # Adjust layout to make room for the table:
        plt.subplots_adjust(left=0.2, bottom=0.2)

        plt.ylabel("People at risk per Return Period")
        plt.yticks(values * value_increment), ['%d' % val for val in values]
        plt.xticks([])
        plt.title('People at risk by Return Period in ' + self.admin)
        plt.show()
