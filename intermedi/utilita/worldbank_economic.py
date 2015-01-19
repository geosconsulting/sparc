__author__ = 'fabio.lana'
import requests

def richieste_wordlBank_dati_eco(iso3_paese):

    ritorno = requests.get('http://api.worldbank.org/countries/' + iso3_paese + '/indicators/NY.GDP.MKTP.CD?date=2006')

    if ritorno.status_code == 200:
        risposta = ritorno.json()
        for valore_mensile in risposta:
            print(valore_mensile)
    else:
        print "Connection failed"

    return ritorno


def chiamate_varie():
    global paese_scelta, paese_iso
    paese_scelta = raw_input("Cameroon/India/Honduras 1/2/3")
    paese_iso = ''
    print paese_scelta
    if paese_scelta == '1':
        paese_iso = 'CMR'
        print(paese_iso)
    elif paese_scelta == '2':
        paese_iso = 'IND'
        print(paese_iso)
    elif paese_scelta == '3':
        paese_iso = 'HND'
        print(paese_iso)
    else:
        print("Errore")
#chiamate_varie()

valori_economici_bancaMondiale_nazionale = richieste_wordlBank_dati_eco('ITA')
