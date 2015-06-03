__author__ = 'fabio.lana'

from owslib.wms import WebMapService
wms = WebMapService('http://localhost:8080/geoserver/wms?', version='1.1.1')
print wms.identification.type, wms.identification.title

#import matplotlib.pyplot as plt
list_layers = list(wms.contents)
for layer in list_layers:
    print layer
print wms.getOperationByName('GetCapabilities').methods

img = wms.getmap(layers=['blueMarble'],
                  srs='EPSG:4326',
                  bbox=(-180, -90, 180, 90),
                  size=(1250, 850),
                  format='image/jpeg',
                  transparent=True
                  )

out = open('img.jpg', 'wb')
out.write(img.read())
out.close()


#imma = plt.imread('img.jpg')
#plt.imshow(imma)
#plt.show()


