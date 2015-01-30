from intermedi.casini.superati import SPARCFlood as SPRC

__author__ = 'fabio.lana'
admin_area_name = "thane"
schema_name = "public"
tabella_pesi = admin_area_name + "_weight"
tabella_pop_stat = admin_area_name + "_pop_stat"
tabella_cicloni = "cyclones"

nuovaConnessione = SPRC
ritorno = nuovaConnessione.UtilitieSparc.paese("India")
ritorno
for recordio in ritorno:
    print recordio
creazione = nuovaConnessione.crea_tabella()[1]
#if creazione == '42P07':
#    nuovaConnessione.cancella_tabella()
#print nuovaConnessione.salva_cambi()
