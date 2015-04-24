import write_shp, write_VRT
__author__ = 'fabio.lana'

import csv

cicloni_file = open('C:/data/jrc/cyclones.csv', 'rb')
cicloni_csv = csv.reader(cicloni_file, delimiter=',', quotechar='"')
colonna_geom = 7

nome_tabella = 'test'
#connessione = write_pgis.connessione()
#write_pgis.scrittura_pgis(connessione,nome_tabella,cicloni_csv,colonna_geom)

try:
    riferimento_file = write_VRT.crea_VRTLayer()
    layer_virtuale = riferimento_file.GetLayer()
    #MODI ALTERNATIVI PER RIFERIRSI AL FILE
    #layer_virtuale = riferimento_file.GetLayer('cyclones_fields')
    #layer_virtuale = riferimento_file[0]
    #VARIE METRICHE DAL FILE NON USATE QUI
    #print layer_virtuale.GetFeatureCount(), layer_virtuale.GetSpatialRef(), layer_virtuale.GetExtent()
except Exception as e:
    print(e.message)

source_shape, file_shp = write_shp.creazione_file()
write_shp.creazione_campi(file_shp)
write_shp.scrittura_valori(layer_virtuale, source_shape, file_shp)


