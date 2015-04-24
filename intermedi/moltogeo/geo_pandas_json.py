__author__ = 'fabio.lana'
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

raw = pd.io.json.read_json('Cronologiadelleposizioni.json')
df = raw['locations'].apply(pd.Series)

# Create a list from the latitude column, multiplied by -E7
df['latitude'] = df['latitudeE7'] * 0.0000001

# Create a list from the longitude column, multiplied by -E7
df['longitude'] = df['longitudeE7'] * 0.0000001

# Create a figure of size (i.e. pretty big)
fig = plt.figure(figsize=(20,10))

map = Basemap(projection='gall',
              # with low resolution,
              resolution = 'l',
              # And threshold 100000
              area_thresh = 100000.0,
              # Centered at 0,0 (i.e null island)
              lat_0=0, lon_0=0)

# Draw the coastlines on the map
map.drawcoastlines()

# Draw country borders on the map
map.drawcountries()

# Fill the land with grey
map.fillcontinents(color = '#888888')

# Draw the map boundaries
map.drawmapboundary(fill_color='#f4f4f4')

# Define our longitude and latitude points
x , y = map(df['longitude'].values, df['latitude'].values)

# Plot them using round markers of size 6
map.plot(x, y, 'ro', markersize=6)

# Show the map
plt.show()