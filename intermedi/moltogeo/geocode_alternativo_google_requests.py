__author__ = 'fabio.lana'
# -*- coding: utf-8 -*-
import pandas as pd
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
geolocator = Nominatim()

def geocode(address, sensor='false'):

    print address
    try:
        mando = str(address.split(",")[1]+ "," + address.split(",")[2])
        print mando
        response = geolocator.geocode(mando, timeout=30)
    except:
        pass

    print response.raw
    return response.raw

def address_to_latlng(address):
    """
    Given a string 'address', return a '(latitude, longitude)' pair.
    """
    location_geo = geocode(address)
    location =  {}
    location['lat'] = location_geo['lon']
    location['lon'] = location_geo['lat']
    print location
    return tuple(location.values())


def basic_world_map(ax=None, region='world'):
    if region=='world':
        m = Basemap(resolution='i',projection='eck4',
                    lat_0=0,lon_0=0)
        # draw parallels and meridians.
        m.drawparallels(np.arange(-90.,91.,30.))
        m.drawmeridians(np.arange(-180.,181.,30.))
    elif region=='europe':
        m = Basemap(width=4000000,height=4000000,
                    resolution='l',projection='aea',\
                    lat_1=40.,lat_2=60,lon_0=10,lat_0=50)
        # draw parallels and meridians.
        m.drawparallels(np.arange(-90.,91.,10.))
        m.drawmeridians(np.arange(-180.,181.,10.))
        m.shadedrelief(scale=0.5)
    m.drawcoastlines()
    m.drawcountries()
    m.fillcontinents(color='coral', alpha=0.3)
    return m

data = pd.DataFrame.from_csv('F1-circuits.csv', header=0, sep=';', index_col=None, parse_dates=False, encoding='latin-1')
maximum = data['Grands Prix held'].max()
minimum = data['Grands Prix held'].min()
f, ax = plt.subplots(figsize=(20, 8))
ax.set_title('Formula 1 Grand Prix Circuits since 1950\n(Radius by number of races held)')
m = basic_world_map(ax)

for cir, loc, num in zip(data['Circuit'].values, data['Location'].values, data['Grands Prix held'].values):
    lat, lng = address_to_latlng(cir + ', ' + loc)
    x, y = m(lat, lng)
    m.scatter(x, y, s=np.pi * (3 + (num-minimum)/(maximum-minimum)*17)**2, marker='o', c='red', alpha=0.7)
f.savefig('f1-circuits.png', dpi=72, transparent=False, bbox_inches='tight')

f, ax = plt.subplots(figsize=(20, 8))
ax.set_title('Formula 1 Grand Prix Circuits in Europe since 1950\n(Radius by number of races held)')
m = basic_world_map(ax, 'europe')
for cir, loc, num in zip(data['Circuit'].values, data['Location'].values, data['Grands Prix held'].values):
    lat, lng = address_to_latlng(cir + ', ' + loc)
    x, y = m(lat, lng)
    m.scatter(x, y, s=np.pi * (3 + (num-minimum)/(maximum-minimum)*17)**2, marker='o', c='red', alpha=0.7)
f.savefig('f1-circuits-europe.png', dpi=72, transparent=False, bbox_inches='tight')