__author__ = 'silvia.calo'
import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt
import pylab
import os
import unicodedata
import re
import collections
import xlwt
from copy import deepcopy
#LOAD the file with GAUL and GADM names for all Admin areas
def load_admin_n_name():
    admin_n_name = {}
    with open("admin_n_name.csv", 'rb') as f:
        tmp = csv.reader(f)
        return [[x.strip() for x in row] for row in tmp]    #delete white spaces before and after the word
        count = 0.0
        for row in tmp:
            if count > 0:  # Misses Header Rows
                GAUL_name = row[4]
                if GAUL_name in PHL_admin2:
                    admin_n_name[GAUL_name] = admin_n_name[GAUL_name] + [row[1]]
                else:
                    admin_n_name[GAUL_name] = [row[1]]
            count += 1
    return admin_n_name
admin_n_name = load_admin_n_name()

#transform all the letters in low letters
admin_n_name_lower = []
admin_n_name_lower = [[x.lower() for x in item] for item in admin_n_name]
#remove unusual characters
for row in range(0,len(admin_n_name_lower)):
    for item in range(0,len(admin_n_name_lower[row])):
        no_dash = re.sub('-', '', admin_n_name_lower[row][item])
        no_space = re.sub(' ', '', no_dash)
        no_slash = re.sub('/', '_', no_space)
        no_apice = re.sub('\'', '', no_slash)
        no_bad_char = re.sub(r'-/\([^)]*\)', '', no_apice)
        unicode_pulito = no_bad_char.decode('latin1')
        admin_n_name_lower[row][item] = unicodedata.normalize('NFKD', unicode_pulito).encode('ascii', 'ignore')
#print admin_n_name_lower
philippines = []
for i in range(0,len(admin_n_name_lower)):
    if admin_n_name_lower[i][1]=='philippines':
        philippines.append(admin_n_name_lower[i])
lista1 = [['0', '2003071500:00:00', '2003071900:00:00', 'philippines', 'storm', 'tropicalcyclone', '8.0', '116602', '1.499', '20030822', 'cordilleraadministrativeregion(car)'], ['0', '2003071500:00:00', '2003071900:00:00', 'philippines', 'storm', 'tropicalcyclone', '8.0', '116602', '1.499', '20030822', 'regionviiieasternvisayas'], ['1', '2003071900:00:00', '2003072300:00:00', 'philippines', 'storm', 'tropicalcyclone', '21.0', '14280', '26.468', '20030346', 'maguindanao'], ['1', '2003071900:00:00', '2003072300:00:00', 'philippines', 'storm', 'tropicalcyclone', '21.0', '14280', '26.468', '20030346', 'autonomousregionofmuslimmindanao']]
lista3 = []
for i in range(0,len(lista1)):
    for j in range(0,len(philippines)):
        if lista1[i][3]==philippines[j][11] and lista1[i][10]==philippines[j][9]:
            lista3.append(lista1[i])

for i in range(0,len(lista1)):
    if lista1[i]not in lista3:
            lista3.append(lista1[i])

ignore_list = []
for i in range(0, len(lista3)):
    for j in range(0,len(philippines)):
            print lista3[i][3], philippines[j][11]
            print lista3[i][10], philippines[j][9]
            if lista3[i][3] == philippines[j][11] and lista3[i][10] == philippines[j][9] and j not in ignore_list:
                index1 = i
                index2 = j
                print index1,index2
                lista3[index1][10] = philippines[index2][7]
                ignore_list = ignore_list + [j]
                break

workbook=xlwt.Workbook(encoding='ascii')
sheet1=workbook.add_sheet('philippines')
sheet2=workbook.add_sheet('lista3')
#sheet3=workbook.add_sheet('philippines')
#sheet4=workbook.add_sheet('emdat_record_clean_admin2')
for i in range(0,len(philippines)):
    for j in range(0,len(philippines[i])):
        sheet1.write(i,j,philippines[i][j])
for i in range(0,len(lista3)):
    for j in range(0,len(lista3[i])):
        sheet2.write(i,j,lista3[i][j])
# for i in range(0,len(philippines)):
#     for j in range(0,len(philippines[i])):
#         sheet3.write(i,j,philippines[i][j])
# for i in range(0,len(emdat_record_clean_admin2)):
#     for j in range(0,len(emdat_record_clean_admin2[i])):
#         sheet4.write(i,j,emdat_record_clean_admin2[i][j])


workbook.save('C:/data/emdat.xls')