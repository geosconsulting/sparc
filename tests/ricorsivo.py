__author__ = 'fabio.lana'

import unicodedata
import re
import dbf
import csv
import os
import shapefile
from osgeo import ogr
ogr.UseExceptions()

class Recorsivo():

    def __init__(self, paese):

        self.paese = paese
        self.proj_dir = os.getcwd() + "/projects/"
        driver = ogr.GetDriverByName("ESRI Shapefile")
        self.shape_countries = "c:/data/tools/sparc/input_data/gaul/gaul_wfp.shp"
        self.campo_nome_paese = "ADM0_NAME"
        self.campo_iso_paese = "ADM0_CODE"
        self.campo_nome_admin = "ADM2_NAME"
        self.campo_iso_admin = "ADM2_CODE"
        self.shapefile = driver.Open(self.shape_countries)
        self.layer = self.shapefile.GetLayer()

    def lista_admin0(self):
        numFeatures = self.layer.GetFeatureCount()
        lista_stati = []
        for featureNum in range(numFeatures):
            feature = self.layer.GetFeature(featureNum)
            nome_paese = feature.GetField(self.campo_nome_paese)
            lista_stati.append(nome_paese)

        seen = set()
        seen_add = seen.add
        lista_pulita = [x for x in lista_stati if not (x in seen or seen_add(x))]
        lista_admin0 = sorted(lista_pulita)
        return lista_admin0

    def lista_admin2(self, paese):

        country_capitalized = paese.capitalize()
        self.layer.SetAttributeFilter(self.campo_nome_paese + " = '" + country_capitalized + "'")

        listone={}
        lista_iso = []
        lista_clean = []
        lista_admin2 = []

        for feature in self.layer:
            cod_admin = feature.GetField(self.campo_iso_admin)
            nome_zozzo = feature.GetField(self.campo_nome_admin)

            unicode_zozzo = nome_zozzo.decode('utf-8')
            nome_per_combo = unicodedata.normalize('NFKD', unicode_zozzo)

            no_dash = re.sub('-', '_', nome_zozzo)
            no_space = re.sub(' ', '', no_dash)
            no_slash = re.sub('/', '_', no_space)
            no_apice = re.sub('\'', '', no_slash)
            no_bad_char = re.sub(r'-/\([^)]*\)', '', no_apice)
            unicode_pulito = no_bad_char.decode('utf-8')
            nome_pulito = unicodedata.normalize('NFKD', unicode_pulito).encode('ascii', 'ignore')

            lista_iso.append(cod_admin)
            lista_clean.append(nome_pulito)
            lista_admin2.append(nome_per_combo)

        for i in range(len(lista_iso)):
            listone[lista_iso[i]] = {'name_orig': lista_admin2[i],'name_clean': lista_clean[i]}

        return lista_admin2, listone

    def creazione_struttura(self, admin_global):

        # Check in data structures exists and in case not create the directory named
        # after the country and all the directories

        os.chdir(self.proj_dir)
        country_low = str(self.paese).lower()
        if os.path.exists(country_low):
           os.chdir(self.proj_dir + country_low)
           admin_low = str(self.admin).lower()
           if os.path.exists(admin_low):
               pass
           else:
              os.mkdir(admin_low)
        else:
            os.chdir(self.proj_dir)
            os.mkdir(country_low)
            os.chdir(self.proj_dir + country_low)
            admin_low = str(self.admin).lower()
            if os.path.exists(admin_low):
                pass
            else:
                os.mkdir(admin_low)

        return "Project created......\n"
paese = "Togo"
generazione_di_fenomeni = Recorsivo()

# for paese in nuova_generazione_di_fenomeni.lista_admin0():
#     print paese
illoli = generazione_di_fenomeni.lista_admin2(paese)[1]

for illo in illoli.iteritems():
    admin_global = illo[1]['name_orig']
    print(paese, admin_global)
    nuovo = Recorsivo(paese)
    nuovo.creazione_struttura(admin_global)
