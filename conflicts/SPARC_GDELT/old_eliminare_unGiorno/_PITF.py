__author__ = 'fabio.lana'
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from osgeo import ogr
ogr.UseExceptions()

xls_file = r"C:\data\tools\sparc\conflicts\data\PITF\pitf.world.19950101-20121231.xls"
xls_pd = pd.ExcelFile(xls_file)
xls_df = pd.DataFrame(xls_pd.parse('Sheet1', skiprows=2))

paesi_presenti = xls_df.groupby(['Country'])

# morti = paesi_presenti['Deaths Number'].unique()
# fig1 = plt.figure(figsize=(15,6))
# ax1 = fig1.add_subplot(111)
# ax1.set_xlabel('Countries')
# ax1.set_ylabel('Deaths')
# ax1.set_title('Deaths By Country')
# morti.plot(kind='bar')
# plt.show()

df_paese = pd.DataFrame(xls_df[xls_df['Country'] == 'SDN'])
df_paese_direction_amended = pd.DataFrame(df_paese.replace(['North', 'South', 'West', 'East'], ['N', 'S', 'W', 'E']))
df_paese_direction_amended_NA_to_zero = pd.DataFrame(df_paese_direction_amended.dropna(subset = ['Degrees', 'Minutes', 'Seconds','Degrees.1', 'Minutes.1', 'Seconds.1']))

def dms2dd(coord):
    d, m, s = coord.split(" ")
    decdeg = float(d)+float(m)/60.+float(s)/3600.
    return decdeg

df_paese_direction_amended_NA_to_zero['latitude'] = df_paese_direction_amended_NA_to_zero['Degrees'].astype(str) + " " \
                                                    + df_paese_direction_amended_NA_to_zero['Minutes'].astype(str) + " " \
                                                    + df_paese_direction_amended_NA_to_zero['Seconds'].astype(str)
                                                    # + " " + df_paese_direction_amended_NA_to_zero['Direction']
df_paese_direction_amended_NA_to_zero['longitude'] = df_paese_direction_amended_NA_to_zero['Degrees.1'].astype(str) + " " \
                                                     + df_paese_direction_amended_NA_to_zero['Minutes.1'].astype(str) + " " \
                                                     + df_paese_direction_amended_NA_to_zero['Seconds.1'].astype(str) #
                                                     # + " " + df_paese_direction_amended_NA_to_zero['Direction.1']
df_paese_direction_amended_NA_to_zero['dd_lat'] = df_paese_direction_amended_NA_to_zero['latitude'].apply(dms2dd)
df_paese_direction_amended_NA_to_zero['dd_lon'] = df_paese_direction_amended_NA_to_zero['longitude'].apply(dms2dd)

#print df_paese_direction_amended_NA_to_zero.head()

lat_mean = df_paese_direction_amended_NA_to_zero['dd_lat'].mean()
lon_mean = df_paese_direction_amended_NA_to_zero['dd_lon'].mean()
lat_min = df_paese_direction_amended_NA_to_zero['dd_lat'].min()
lon_min = df_paese_direction_amended_NA_to_zero['dd_lon'].min()
lat_max = df_paese_direction_amended_NA_to_zero['dd_lat'].max()
lon_max = df_paese_direction_amended_NA_to_zero['dd_lon'].max()

# shp_file = '../../input_data/countries/Angola.shp'
# angola = gpd.GeoDataFrame.from_file(shp_file)
# angola.plot()
# plt.show()

# Create a figure of size (i.e. pretty big)
fig = plt.figure(figsize=(10,5))
map = Basemap(projection='gall',
              # with low resolution,
              resolution = 'l',
              # And threshold 100000
              area_thresh = 1000.0,
              # Centered at 0,0 (i.e null island)
              lat_0=lat_mean, lon_0=lon_mean,
              llcrnrlon=lon_min-5, llcrnrlat=lat_min-5,
              urcrnrlon=lon_max+5, urcrnrlat=lat_max+5)

map.drawcoastlines()
map.drawcountries()
map.drawmapboundary(fill_color='lightblue')
map.drawparallels(np.arange(0.,90.,5.),color='gray',dashes=[1,3],labels=[1,0,0,0])
map.drawmeridians(np.arange(0.,360.,10.),color='gray',dashes=[1,3],labels=[0,0,0,1])
map.fillcontinents(color='beige',lake_color='lightblue')

lista_tipi_eventi = df_paese['Event Type'].unique()
lista_tipi_eventi = set([str(evento).strip() for evento in lista_tipi_eventi])

x, y = map(df_paese_direction_amended_NA_to_zero['dd_lon'].values,
             df_paese_direction_amended_NA_to_zero['dd_lat'].values)
map.plot(x, y, 'ro', markersize=6)

plt.show()



