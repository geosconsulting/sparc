__author__ = 'fabio.lana'

import matplotlib.pyplot as plt
import pylab
import collections

class Classicaccio(object):

    def __init__(self, paese, file_incidenti):
        self.paese = paese
        self.historical_accidents_file = file_incidenti

    def missing_months(self, dict_ordinato):
        missing = []
        for indice in range(1, 13):
            if indice not in dict_ordinato:
                missing.append(indice)
        for valore in missing:
            dict_ordinato[valore] = 0
        danni_completati = collections.OrderedDict(sorted(dict_ordinato.items()))
        return danni_completati

    def historical_analysis_damages(self):

        file_incidenti_in = open(self.historical_accidents_file)
        next(file_incidenti_in)
        mesi = []
        for linea in file_incidenti_in:
            splittato_comma = linea.split(",")
            if splittato_comma[2] == self.paese:
                splittato_mese_inzio = splittato_comma[0].split("/")
                splittato_mese_fine = splittato_comma[1].split("/")
                differenza = int(splittato_mese_fine[1]) - int(splittato_mese_inzio[1])
                if differenza==0:
                     mesi.append(int(splittato_mese_inzio[1]))
                else:
                    mesi.append(int(splittato_mese_inzio[1]))
                    for illo in range(1,differenza+1):
                        mesi.append(int(splittato_mese_inzio[1])+illo)
                print "Tra %s e %s ho %d" % (splittato_mese_fine[1],splittato_mese_inzio[1],differenza)

        file_incidenti_in.close()

        conta_mesi = collections.Counter(mesi)
        conta_mesi_ord = collections.OrderedDict(sorted(conta_mesi.items()))

        return conta_mesi_ord

    def plot_monthly_danni(self, danni_mesi):

        fig = pylab.gcf()
        fig.canvas.set_window_title("Historical Envents")

        plt.grid(True)

        # Plot y1 vs x in blue on the left vertical axis.
        plt.xlabel("Months")
        plt.ylabel("Historical Incidents related with Floods EM-DAT", color="b")
        plt.tick_params(axis="y", labelcolor="b")
        plt.bar(range(len(danni_mesi)), danni_mesi.values(), align='center', color='g',label='Incidents')
        plt.xticks(range(len(danni_mesi)), danni_mesi.keys())

        plt.title(self.paese)
        plt.legend()
        plt.show()


file_flood = "c:/data/input_data/historical_data/floods - refine.csv"
paese = Classicaccio("India",file_flood)
mesi = paese.historical_analysis_damages()
mesi_plot = paese.missing_months(mesi)
print mesi_plot
paese.plot_monthly_danni(mesi_plot)