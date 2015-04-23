__author__ = 'fabio.lana'
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

xls_file = r"C:\data\tools\sparc\conflicts\data\PITF\pitf.world.19950101-20121231.xls"
xls_pd = pd.ExcelFile(xls_file)
xls_df = pd.DataFrame(xls_pd.parse('Sheet1', skiprows=2))

paesi_presenti = xls_df.groupby(['Country'])
#print paesi_presenti['Country'].unique()
morti = paesi_presenti['Deaths Number'].unique()

# fig1 = plt.figure(figsize=(15,6))
# ax1 = fig1.add_subplot(111)
# ax1.set_xlabel('Countries')
# ax1.set_ylabel('Deaths')
# ax1.set_title('Deaths By Country')
# morti.plot(kind='bar')
#plt.show()

#BOXPLOT DEI DATI DI DENSITA
df_paese = pd.DataFrame(xls_df[xls_df['Country'] == 'SYR'])
df_paese_direction_amended = pd.DataFrame(df_paese.replace(['North','South','West','East'],['N','S','W','E']))

##GEOCODIFICA
import LatLon
#NGA Kano	12 0 0 N,8 31 0 E
lat = '12 0 0 N'
lon = '8 31 0 E'
Kano = str(LatLon.string2latlon(lat, lon, 'd% %m% %S% %H')).split(",")
#print "Lat %0.4f Lon %0.4f per Kano" % (float(Kano[0]),float(Kano[1]))

def dms2dd(coord):

    d, m, s = coord.split(" ")

    decdeg = float(d)+float(m)/60.+float(s)/3600.
    return decdeg
#print dms2dd(8,31,0)

df_paese_direction_amended['latitude'] = df_paese_direction_amended['Degrees'].astype(str) + " " + df_paese_direction_amended['Minutes'].astype(str) + " " + df_paese_direction_amended['Seconds'].astype(str) # + " " + de_paese_direction_amended['Direction']
df_paese_direction_amended['longitude'] = df_paese_direction_amended['Degrees.1'].astype(str) + " " + df_paese_direction_amended['Minutes.1'].astype(str) + " " + df_paese_direction_amended['Seconds.1'].astype(str) # + " " + de_paese_direction_amended['Direction.1']
df_paese_direction_amended['dd_lat'] = df_paese_direction_amended['latitude'].apply(dms2dd)
df_paese_direction_amended['dd_lon'] = df_paese_direction_amended['longitude'].apply(dms2dd)

print df_paese_direction_amended.head()



