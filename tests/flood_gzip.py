__author__ = 'fabio.lana'
import os
import gzip
import csv
import unicodedata
import re

rootdir = "d:/flood_download/extracted/"
exportdir_m1 = "d:/flood_download/final/m1/"
exportdir_m2 = "d:/flood_download/final/m2/"

def controlla(paese_letto):

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
#         messaggio = controlla(paese_letto)

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

import pycountry
paese = pycountry.countries.get(alpha3='TLS')
print paese.name, paese.alpha2
# for admin in pycountry.subdivisions.get(country_code=paese.alpha2):
#     print admin.name
