__author__ = 'fabio.lana'
import requests
import all_plots

def richiesta_vam(adm0,adm1,adm2):

    richiesta_txt = requests.get('http://reporting.vam.wfp.org/JSON/SPARC_GetFCS.aspx?adm0=' +
                                 str(adm0) + '&adm1=' + str(adm1) + '&adm2=' + str(adm2) + '&adm3=0&adm4=0&adm5=0&indTypeID=1')

    if richiesta_txt.status_code == 200:
        print("Server Responding..." + str(richiesta_txt.status_code))
        risposta = richiesta_txt.json()
    else:
        print "Connection failed"

    return risposta

#http://reporting.vam.wfp.org/JSON/SPARC_GetFCS.aspx ?adm0=40764&adm1=2758&adm2=37047&adm3=0&adm4=0&adm5=0&indTypeID=1&startMonth=1&startYear=2011&endMonth=12&endYear=2013
adm0 = 40764
adm1 = 27568
adm2 = 37047
adm3 = 0
adm4 = 0
adm5 = 0
indTypeID = 1
startMonth = 1
startYear = 2011
endMonth = 12
endYear = 2013

print richiesta_vam(adm0,adm1,adm2)