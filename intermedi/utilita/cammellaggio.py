__author__ = 'fabio.lana'
import os, glob

def selezioniamo_rasters(direttorio):

    lista_rasters = []
    for direttorio_principale, direttorio_secondario,file_corrente in os.walk(direttorio):
        print file_corrente
        files_tif = glob.glob(direttorio_principale + "/*.tif")
        for file_tif in files_tif:
            fileName, fileExtension = os.path.splitext(file_tif)
            lista_rasters.append(fileName + fileExtension)

    return lista_rasters
dir_base = "C:/data/_archivio/admin areas/g2014_2013_2_mid"
lista_rasters_invio = selezioniamo_rasters(dir_base)

