__author__ = 'fabio.lana'
import requests
import all_plots

def richieste_wordlBank(iso3_paese):
    r_1980_1999 = requests.get('http://climatedataapi.worldbank.org/climateweb/rest/v1/country/mavg/pr/1980/1999/' + iso3_paese)

    lista_valori_mensili_pioggia = []

    if r_1980_1999.status_code == 200:
        risposta = r_1980_1999.json()
        for valore_mensile in risposta[0]['monthVals']:
            lista_valori_mensili_pioggia.append(valore_mensile)
    else:
        print "Connection failed"

    return lista_valori_mensili_pioggia

def historical_analysis_damages(paese):

        import collections

        file_incidenti_in = open("c:/data/tools/sparc/input_data/historical_data/floods - refine.csv")
        next(file_incidenti_in)
        mesi = []
        for linea in file_incidenti_in:
            splittato_comma = linea.split(",")
            if splittato_comma[2] == paese:
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

        return danni_mesi

paese_iso = 'TGO'
paese_nome = 'Togo'
valori_precipitazione_bancaMondiale_nazionale = richieste_wordlBank(paese_iso)
ivaloraggi = all_plots.plot_monthly_mean_wb(paese_iso, valori_precipitazione_bancaMondiale_nazionale)
dict_finale = historical_analysis_damages(paese_nome)
labella_y = "Precipitation (mm) Real Time World Bank"
all_plots.plot_monthly_danni("EM-DAT Registered Incidents", labella_y, paese_iso, ivaloraggi, dict_finale)