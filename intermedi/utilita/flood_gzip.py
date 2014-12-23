__author__ = 'fabio.lana'
import os
import gzip
import csv
import unicodedata
import re

rootdir = "d:/flood_download/extracted/"
exportdir_m1 = "d:/flood_download/final/m1/"
exportdir_m2 = "d:/flood_download/final/m2/"

def pulisci_nome():

    tabella = "Flood_Colombia_desinventar_FAB.csv"
    with open(tabella, 'rb') as csvfile:
        luoghi_splittati = csv.reader(csvfile, delimiter=",", quotechar='"')
        for row in luoghi_splittati:
            nome_zozzo = row[2]
            no_dash = re.sub('-', '_', nome_zozzo)
            no_space = re.sub(' ', '', no_dash)
            no_slash = re.sub('/', '_', no_space)
            no_apice = re.sub('\'', '', no_slash)
            no_bad_char = re.sub(r'-/\([^)]*\)', '', no_apice)
            unicode_pulito = no_bad_char.decode('utf-8')
            nome_pulito = unicodedata.normalize('NFKD', unicode_pulito).encode('ascii', 'replace')
            print nome_pulito

#pulisci_nome()

def scompatta_gzip(paese_letto):

    print "Chiamata funzione con %s" % paese_letto

    for subdir, dirs, files in os.walk(rootdir):
        finale = subdir.split("/")[3]
        paese = finale.split("\\")[0]
        if str(paese) == paese_letto.strip():
            for file in files:
                fileName, fileExtension = os.path.splitext(file)
                if fileExtension == '.gz':
                    rp = finale.split("\\")[1]
                    M = (fileName.split("_")[1]).split(".")[0]
                    infile = rootdir + paese + "/" + rp + "/" + file
                    if M == "M1":
                        outfilename = exportdir_m1 + paese + "_" + rp + "_" + M + ".grd"
                    else:
                        outfilename = exportdir_m2 + paese + "_" + rp + "_" + M + ".grd"
                    print outfilename
                    inF = gzip.open(infile, 'rb')
                    outF = open(outfilename, 'wb')
                    outF.write(inF.read())
                    inF.close()
                    outF.close()

# with open("wfpcountries.txt") as sparc:
#     contatore = 0
#     for paese_letto in sorted(sparc):
#         messaggio = scompatta_gzip(paese_letto)

import pycountry
#wfp_countries_all_data = open("wfp_countries_data.txt", "wb")
with open("wfpcountries.txt") as sparc:
    contatore = 0
    for paese_letto in sorted(sparc):
        try:
            dati_paese = pycountry.countries.get(name=paese_letto.rstrip('\n'))
            #data = dati_paese.name + "," + dati_paese.official_name + "," + dati_paese.alpha2 + "," + dati_paese.alpha3 #+ "\n"
            #wfp_countries_all_data.write(data)
            #print data
        except:
            #print "Non trovato " + paese_letto
            pass
# for admin in pycountry.subdivisions.get(country_code=paese.alpha2):
#     print admin.name

dati_paese = pycountry.countries.get(alpha2="TM")
data = dati_paese.name +  ","  + dati_paese.alpha2 + "," + dati_paese.alpha3 + "\n"
print data

#+ dati_paese.official_name + ","

# todo_mundo = list(pycountry.countries)
# for illo in todo_mundo:
#      print illo.name