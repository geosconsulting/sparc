__author__ = 'fabio.lana'

import geocode_csv_shp

#nuova_geocodifica = geocode_csv_shp.GeocodeCsv("Swaziland")
#nuova_geocodifica.geolocate_accidents()
#nuova_geocodifica.create_validated_coords()

nuovo_shp_geocodificato = geocode_csv_shp.CreateGeocodedShp("Swaziland")
nuovo_shp_geocodificato.creazione_file_shp()


