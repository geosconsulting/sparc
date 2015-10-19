def plot_mappa(paese):

    def GetExtent(gt,cols,rows):
        ext=[]
        xarr = [0, cols]
        yarr = [0, rows]

        for px in xarr:
            for py in yarr:
                x=gt[0]+(px*gt[1])+(py*gt[2])
                y=gt[3]+(px*gt[4])+(py*gt[5])
                ext.append([x,y])
                #print x,y
            yarr.reverse()
        return ext


    pathToRaster = "input_data/geocoded/risk_map/" + paese + ".tif"
    from mpl_toolkits.basemap import Basemap
    import matplotlib.pyplot as plt
    import numpy as np
    from osgeo import gdal

    raster = gdal.Open(pathToRaster, gdal.GA_ReadOnly)
    array = raster.GetRasterBand(1).ReadAsArray()
    msk_array = np.ma.masked_equal(array, value=65535)
    # print 'Raster Projection:\n', raster.GetProjection()
    geotransform = raster.GetGeoTransform()
    cols = raster.RasterXSize
    rows = raster.RasterYSize
    ext = GetExtent(geotransform, cols, rows)
    #print ext[1][0], ext[1][1]
    #print ext[3][0], ext[3][1]

    #map = Basemap(projection='merc',llcrnrlat=-80, urcrnrlat=80, llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c')
    map = Basemap(projection='merc', llcrnrlat=ext[1][1], urcrnrlat=ext[3][1], llcrnrlon=ext[1][0], urcrnrlon=ext[3][0],lat_ts=20, resolution='c')

    # Add some additional info to the map
    map.drawcoastlines(linewidth=1.3, color='white')
    #map.drawrivers(linewidth=.4, color='white')
    map.drawcountries(linewidth=.75, color='white')
    #datain = np.flipud(msk_array)
    datain = np.flipud(msk_array)
    map.imshow(datain)#,origin='lower',extent=[ext[1][0], ext[3][0],ext[1][1],ext[3][1]])

    plt.show()

#plot_mappa("India")