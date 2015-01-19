__author__ = 'fabio.lana'
import requests
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def richiesta_vam(adm0,adm1,adm2,indTypeID):

    richiesta_txt = requests.get('http://reporting.vam.wfp.org/JSON/SPARC_GetFCS.aspx?adm0=' +
                                 str(adm0) + '&adm1=' + str(adm1) + '&adm2=' + str(adm2) + '&adm3=0&adm4=0&adm5=0&indTypeID='+ str(indTypeID))

    if richiesta_txt.status_code == 200:
        print("Server Responding..." + str(richiesta_txt.status_code))
        risposta = richiesta_txt.json()
    else:
        print "Connection failed"

    return risposta

#http://reporting.vam.wfp.org/JSON/SPARC_GetFCS.aspx ?adm0=239&adm1=2848&adm2=0&adm3=0&adm4=0&adm5=0&indTypeID=1
adm0 = 239
adm1 = 2848
adm2 = 0
adm3 = 0
adm4 = 0
adm5 = 0
indTypeID = 1
startMonth = 1
startYear = 2000
endMonth = 12
endYear = 2014

ritornati = richiesta_vam(adm0, adm1, adm2, indTypeID)

lista_mesi = []
lista_anni = []
lista_fcs = []

for indice in range(0, len(ritornati)):
    lista_mesi.append(ritornati[indice]['FCS_month'])
    lista_anni.append(ritornati[indice]['FCS_year'])
    lista_fcs.append(str(ritornati[indice]['FCS_poor']))
#print ritornati[0]['Methodology']

print lista_mesi
print lista_anni
print lista_fcs

plt.plot(lista_anni, lista_fcs)
plt.xticks(lista_anni)
#plt.show()

matrice = pd.DataFrame(lista_mesi)
