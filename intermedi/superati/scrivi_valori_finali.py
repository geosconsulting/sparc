__author__ = 'fabio.lana'

persone_pesi = {'25': {1: 0.0, 2: 0.0, 3: 738.7643372551656, 4: 2520.490091811741, 5: 10820.72470450213, 6: 283598.5920545418, 7: 662497.783615, 8: 448256.1258110019, 9: 240880.63067090488, 10: 53973.25334534798, 11: 10603.441075897668, 12: 2563.9468175326338},
                '200': {1: 0.0, 2: 0.0, 3: 88.25679340114792, 4: 301.111412780387, 5: 1292.702444522696, 6: 33880.225513875965, 7: 79145.5773765, 8: 53551.1072901671, 9: 28776.906224856644, 10: 6447.937494366218, 11: 1266.7445641105935, 12: 306.3029888628075},
                '50': {1: 0.0, 2: 0.0, 3: 82.89648324780583, 4: 282.82329578663166, 5: 1214.1896663943326, 6: 31822.497039716523, 7: 74338.6404184, 8: 50298.6602765363, 9: 27029.129802505162, 10: 6056.319540810285, 11: 1189.8083477920366, 12: 287.69955950709084},
                '100': {1: 0.0, 2: 0.0, 3: 77.12806277533619, 4: 263.1428024099705, 5: 1129.6992724152183, 6: 29608.10221599082, 7: 69165.72453, 8: 46798.58632515251, 9: 25148.285409628734, 10: 5634.885527468678, 11: 1107.014548069531, 12: 267.6797472791079},
                '500': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0},
                '1000': {1: 0.0, 2: 207.74824508140375, 3: 708.7881302777304, 4: 3042.9007661923256, 5: 79750.88514124947, 6: 186301.293898, 7: 126054.30282439291, 8: 67738.14838154241, 9: 15177.84237594726, 10: 2981.7983411683826, 11: 721.0086152825189, 12: 0.0}}

sequenza = []
for linea in persone_pesi.iteritems():
    linea_rp = linea[0]
    print linea_rp
    for i in range(1,12):
        linea_val = linea[1][i]
        print linea_val