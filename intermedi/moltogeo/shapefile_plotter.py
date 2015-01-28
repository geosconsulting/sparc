from osgeo import ogr
import numpy as np
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

# Extract first layer of features from shapefile using OGR
ds = ogr.Open('c:/data/tools/sparc/input_data/countries/Afghanistan.shp')

nlay = ds.GetLayerCount()
lyr = ds.GetLayer(0)

# Get extent and calculate buffer size
ext = lyr.GetExtent()
xoff = (ext[1]-ext[0])/50
yoff = (ext[3]-ext[2])/50

# Prepare figure
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlim(ext[0]-xoff,ext[1]+xoff)
ax.set_ylim(ext[2]-yoff,ext[3]+yoff)

paths = []
lyr.ResetReading()

# Read all features in layer and store as paths
for feat in lyr:
    geom = feat.geometry()
    codes = []
    all_x = []
    all_y = []
    for i in range(geom.GetGeometryCount()):
        # Read ring geometry and create path
        r = geom.GetGeometryRef(i)
        x = [r.GetX(j) for j in range(r.GetPointCount())]
        y = [r.GetY(j) for j in range(r.GetPointCount())]
        # skip boundary between individual rings
        codes += [mpath.Path.MOVETO] + \
                     (len(x)-1)*[mpath.Path.LINETO]
        all_x += x
        all_y += y
    path = mpath.Path(np.column_stack((all_x,all_y)), codes)
    paths.append(path)

# Add paths as patches to axes
for path in paths:
    patch = mpatches.PathPatch(path, \
            facecolor='blue', edgecolor='black')
    ax.add_patch(patch)

ax.set_aspect(1.0)
plt.show()