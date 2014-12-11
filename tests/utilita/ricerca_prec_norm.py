__author__ = 'fabio.lana'

__author__ = 'fabio.lana'
import os
import psycopg2
import csv


schema = 'public'
dbname = 'geonode-imports'
user = 'geonode'
password = 'geonode'
connection_string = "dbname=%s user=%s password=%s" % (dbname, user, password)
direttorio_radice = "C:/data/tools/sparc/projects/"

def becca_i_csv_vuoti(paese_ricerca):

    direttorio = direttorio_radice + paese_ricerca
    lista_vuoti = []

    for direttorio_principale, direttorio_secondario, files in os.walk(direttorio):
        if direttorio_principale != direttorio:
            #print direttorio_principale
            paese = direttorio_principale.split("/")[5].split("\\")[0]
            admin = direttorio_principale.split(paese)[1][1:]
            for file in files:
                fileName, fileExtension = os.path.splitext(file)
                if fileExtension == '.csv':
                    if fileName.count("_") == 2:
                        file_completo_norm = str(direttorio + "/" + admin + "/" + fileName + ".csv")
                        with open(file_completo_norm, 'rb') as csvlettura:
                            numero_valori = len(csvlettura.readlines())
                            if numero_valori==0:
                                lista_vuoti.append(file_completo_norm)
                                csvlettura.close()
                                with open(file_completo_norm, 'wb') as csvscrittura:
                                    scrittore = csv.writer(csvscrittura, delimiter=',')
                                    data = [['1', 0],
                                            ['2', 0],
                                            ['3', 0],
                                            ['4', 0],
                                            ['5', 0],
                                            ['6', 0],
                                            ['7', 0],
                                            ['8', 0],
                                            ['9', 0],
                                            ['10', 0],
                                            ['11', 0],
                                            ['12', 0]]
                                    scrittore.writerows(data)
    return lista_vuoti


with open("C:/data/tools/sparc/projects/lista.txt") as fileggio:
   paesi = [linea.strip() for linea in fileggio]

#VALORI POPOLAZIONE TEMPO RITORNO
# for paese in paesi:
#     paese_ricerca = paese.title()
#     print paese_ricerca
#     ritornati = becca_il_csv(paese_ricerca)
#VALORI POPOLAZIONE TEMPO RITORNO

paese_ricerca = 'Yemen'
ritornati = becca_i_csv_vuoti(paese_ricerca)
print ritornati


