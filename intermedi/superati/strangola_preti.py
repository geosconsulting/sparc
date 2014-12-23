__author__ = 'fabio.lana'

variabile = {'region iv (southern tagalog)': [
    ['14', '1970-08-31 00:00:00', '1970-08-31 00:00:00', 'philippines', 'storm', 'tropical cyclone', '137.0', 145200.0, '2353.0', '1970-0043', 'region iv (southern tagalog)'],
    ['16', '1970-11-19 00:00:00', '1970-11-19 00:00:00', 'philippines', 'storm', 'tropical cyclone', '786.0', 432075.0, '97656.0', '1970-0064', 'region iv (southern tagalog)']
    ],
    'region ix (zamboanga peninsula)': [
    ['14', '1970-08-31 00:00:00', '1970-08-31 00:00:00', 'philippines', 'storm', 'tropical cyclone', '137.0', 145200.0, '2353.0', '1970-0043', 'region ix (zamboanga peninsula)']
    ]
}

chiavi = variabile.keys()
for illo in range(0, len(chiavi)):
    valori = variabile[chiavi[illo]]
    for valore in range(0,len(valori)):
        print "Successo un %s in data %s nelle %s" % (valori[valore][4],valori[valore][1],valori[valore][3])
