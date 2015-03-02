__author__ = 'fabio.lana'

import gdal
import gdalnumeric

path = 'c:/data/tools/sparc/input_data/drought/SPARC/DSIMonthlyFreq_tiff/'
nome_file = 'wldds9freq11dd.tif'

ds = gdal.Open(path + nome_file)
print ds.GetMetadata()

cols = ds.RasterXSize
rows = ds.RasterYSize
bands = ds.RasterCount

print cols,rows

geotransform = ds.GetGeoTransform()
originX = geotransform[0]
originY = geotransform[3]
pixelWidth = geotransform[1]
pixelHeight = geotransform[5]

print originX
print originY
print pixelWidth
print pixelHeight

ds_np = gdalnumeric.LoadFile(path + nome_file)
print ds_np.shape
import pandas

ds_ps = pandas.DataFrame(ds_np)

print ds_ps