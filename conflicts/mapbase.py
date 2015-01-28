__author__ = 'fabio.lana'

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

m = Basemap(projection='merc',
                    resolution='l', area_thresh=1000.0, # Low resolution
                    lat_0 = 15, lon_0= 30, # Map center
                    llcrnrlon=10, llcrnrlat=1, # Lower left corner
                    urcrnrlon=50, urcrnrlat=30) # Upper right corner
m.drawcoastlines()
m.drawcountries()
m.fillcontinents(color='0.8') # Light gray
m.drawmapboundary()
plt.show()
