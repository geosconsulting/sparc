__author__ = 'fabio.lana'

from owslib.wms import WebMapService
wms = WebMapService('http://10.11.40.84/geoserver/wms?', version='1.1.1')
print wms.identification.type,wms.identification.title

list_layers = list(wms.contents)
for layer in list_layers:
    print layer

#print wms.getOperationByName('GetCapabilities').methods
#print wms.getcapabilities()

# img = wms.getmap(layers=['f_bgd'],
#                   srs='EPSG:4326',
#                   bbox=(-112, 36, -106, 41),
#                   size=(300, 250),
#                   format='image/jpeg',
#                   transparent=True
#                   )
#
# out = open('bangladesh_flood.jpg', 'wb')
# out.write(img.read())
# out.close()