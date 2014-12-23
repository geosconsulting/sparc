__author__ = 'fabio.lana'
import requests

def richiesta_vam(iso3_paese):

    risposta = requests.get('http://reporting.vam.wfp.org/JSON/SPARC_GetFCS.aspx ?adm0=' + 43 + '&adm1=0&adm2=0&adm3=0&adm4=0&adm5=0&indTypeID=1 ')

    lista_valori_mensili_pioggia = []

    if r_1980_1999.status_code == 200:
        risposta = r_1980_1999.json()
        for valore_mensile in risposta[0]['monthVals']:
            lista_valori_mensili_pioggia.append(valore_mensile)
    else:
        print "Connection failed"

    return lista_valori_vam


paese_iso = 'TGO'
paese_nome = 'Togo'
valori_precipitazione_bancaMondiale_nazionale = richiesta_vam(paese_iso)
ivaloraggi = all_plots.plot_monthly_mean_wb(paese_iso, valori_precipitazione_bancaMondiale_nazionale)
dict_finale = richiesta_vam(paese_nome)
labella_y = "Precipitation (mm) Real Time World Bank"
all_plots.plot_monthly_danni("EM-DAT Registered Incidents", labella_y, paese_iso, ivaloraggi, dict_finale)