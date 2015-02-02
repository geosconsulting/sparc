__author__ = 'fabio.lana'

in_file = open("out.txt", "r")
for linea in in_file:
    lat = linea.split("\t")[9]
    lon = linea.split("\t")[10]
    print lat,lon
in_file.close()
