__author__ = 'fabio.lana'
import pandas as pd
import matplotlib.pyplot as plt

csv_file = r"C:\data\tools\sparc\conflicts\data\SCAD\Africa\SCAD 3.1 For Public Release\SCAD 3.1 (For Public Release).csv"
csv_pd = pd.read_csv(csv_file)
#print csv_pd.head()
#print csv_pd.columns

paesi_presenti = csv_pd.groupby(['countryname'])
#print paesi_presenti.head()
morti = paesi_presenti['ndeath'].count()
#print morti.head()

#fig1 = plt.figure(figsize=(15,6))
# ax1 = fig1.add_subplot(111)
# ax1.set_xlabel('Countries')
# ax1.set_ylabel('Deaths')
# ax1.set_title('Deaths By Country')
# morti.plot(kind='bar')
#plt.show()

#csv_pd.boxplot(column='ndeath', by = 'countryname')
#plt.show()

df_kenya = csv_pd[csv_pd['countryname'] == 'Kenya']
ct_kenya = pd.crosstab(df_kenya['styr'],df_kenya['ndeath'].sum())
ct_kenya.plot(kind='bar', stacked = False, grid=True)
plt.show()