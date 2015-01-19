__author__ = 'fabio.lana'
import pandas as pd
from pandas.io import wb
import pycountry
import numpy as np

indicators = ['NY.GDP.PCAP.KD','SP.POP.TOTL', 'SP.POP.0014.TO.ZS', 'SP.POP.65UP.TO.ZS','AG.LND.AGRI.ZS','AG.YLD.CREL.KG','SP.RUR.TOTL','SH.STA.MALN.ZS'
    ,'GC.BAL.CASH.GD.ZS', 'NE.EXP.GNFS.ZS', 'NE.IMP.GNFS.ZS']
nazione = pycountry.countries.get(alpha3='CMR')
iso2 = nazione.alpha2
dati_nazionali = wb.download(indicator=indicators, country=[iso2], start=2006, end=2013)
dati_nazionali.columns = ['GDP Capita','Total Pop','Pop Age 0-14','Pop Age 65-up',
                'Perc Agr Land','Cereal Yeld','Rural Population','Malnutrition Age<5',
                'Cash Surplus-Deficit','Export', 'Import', ]
#print dati['NY.GDP.PCAP.KD'].groupby(level=0).mean()

dati_nazionali['Importer'] = dati_nazionali['Export'] - dati_nazionali['Import']
print dati_nazionali

# sub_indicators = ['SI.POV.NAHC','SI.POV.RUHC', 'SI.POV.URHC']
# dati_sub_national = wb.download(indicator=indicators, country=[iso2], start=2006, end=2013)
# print dati_sub_national