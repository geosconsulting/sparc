#!/usr/bin/python

from dbfpy import dbf
import os
import glob

def prepare_drought_tables(paese):

    direttorio_radice = r"C:\data\tools\sparc\projects\drought"
    direttorio = direttorio_radice + "\\" + paese_ricerca

    import pycountry
    iso_paese = pycountry.countries.get(name=paese_ricerca).alpha3

    lista = []
    for direttorio_principale, direttorio_secondario, file_vuoto in os.walk(direttorio):
        if direttorio_principale != direttorio:
            name_adm = direttorio_principale.split("\\")[7].split("_")[0]
            code_adm = direttorio_principale.split("\\")[7].split("_")[1]
            files_dbf = glob.glob(direttorio_principale + "/*.dbf")
            for file in files_dbf:
                fileName, fileExtension = os.path.splitext(file)
                if 'stat' in fileName:
                    try:
                        if str(fileExtension) == '.dbf':
                            temporal_string = fileName.split("\\")[-1].split("_")[1]
                            temporal_value = ''.join(x for x in temporal_string if x.isdigit())
                            in_dbf = dbf.Dbf(fileName + fileExtension)
                            for rec in in_dbf:
                                stringola = (paese, iso_paese, name_adm, code_adm, temporal_value, rec['VALUE'], rec['SUM'])
                                lista.append(stringola)
                            in_dbf.close()
                    except:
                        pass
    return lista

paese_ricerca = "Pakistan"
print prepare_drought_tables(paese_ricerca)
