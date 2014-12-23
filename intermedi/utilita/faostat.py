__author__ = 'fabio.lana'

from pandas import DataFrame, read_csv

import pandas as pd
import matplotlib.pyplot as plt

file_popolazione = str(r"C:\data\tools\sparc\input_data\faostat\Population_E_All_Data.csv")
df_popolazione = pd.read_csv(file_popolazione,index_col=0,header=0)
#print df_popolazione.info()
#print df_popolazione.dtypes
#print df_popolazione.head(10)

solo_necessari = df_popolazione[['Country','Element','Year','Value']]
per_paese = solo_necessari[solo_necessari['Country'] == 'Italy'][:55]
element = per_paese.groupby('Element')
per_paese_per_anno = per_paese.set_index('Year')
per_paese_per_anno.max()

maskera = per_paese['Element'] == 'Total Population - Both sexes'
adesso = per_paese[maskera]
pop_61 = adesso[['Year', 'Value']][adesso['Year'] <= 2015]
lista_anni = list(pop_61['Year'])
print lista_anni
cambio = pop_61.set_index('Year')
print cambio.head(5)

plt.plot(cambio)
plt.grid()
plt.xticks(range(len(lista_anni)),lista_anni, rotation = 'vertical')
plt.show()

#EXPORT DATA FRAME
cambio.to_excel("cambio.xls")
cambio.to_csv("cambio.txt")
cambio.to_json("cambio.json")
