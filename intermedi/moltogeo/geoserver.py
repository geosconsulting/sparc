__author__ = 'fabio.lana'

from owslib.wms import WebMapService
wms = WebMapService('http://sedac.ciesin.columbia.edu/geoserver/wms?', version='1.1.1')
print wms.identification.type, wms.identification.title

list_layers = list(wms.contents)
for layer in list_layers:
    print layer

#print wms.getOperationByName('GetCapabilities').methods
#print wms.getcapabilities()

# img = wms.getmap(layers=['grump-v1-population-density_2000'],
#                   srs='EPSG:4326',
#                   bbox=(-112, 36, -106, 41),
#                   size=(300, 250),
#                   format='image/jpeg',
#                   transparent=True
#                   )
#
# out = open('grump-v1-population-density_2000.jpg', 'wb')
# out.write(img.read())
# out.close()
