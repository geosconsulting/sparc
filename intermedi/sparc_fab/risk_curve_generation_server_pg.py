__author__ = 'fabio.lana'
import matplotlib.pyplot as plt
import psycopg2 as pg
import psycopg2.extras
from matplotlib import pylab
import collections

def hazardIntensity_damageData(adm2_code):

    schema = 'public'
    dbname = 'geonode-imports'
    user = 'geonode'
    password = 'geonode'

    try:
        connection_string = "dbname=%s user=%s password=%s" % (dbname, user, password)
        conn = pg.connect(connection_string)
    except Exception as e:
         print e.message

    cursor = conn.cursor('cursor_unique_name', cursor_factory=pg.extras.DictCursor)
    comando = "SELECT c.rp25,c.rp50,c.rp100,c.rp200,c.rp500,c.rp1000 FROM SPARC_annual_pop c WHERE c.adm2_code = '" + str(adm2_code) + "';"

    cursor.execute(comando)
    row_count = 0
    dict_damages = {}
    for row in cursor:
        row_count += 1
        dict_damages[4.0] = row[0]
        dict_damages[2.0] = row[0] + row[1]
        dict_damages[1.0] = row[0] + row[1] + row[2]
        dict_damages[0.5] = row[0] + row[1] + row[2] + row[3]
        dict_damages[0.2] = row[0] + row[1] + row[2] + row[3] + row[4]
        dict_damages[0.1] = row[0] + row[1] + row[2] + row[3] + row[4] + row[5]

    return dict_damages

def plotVulnerabilityCurve(dati_db):

    eccolo = collections.OrderedDict(sorted(dati_db.items(),reverse=False))
    print eccolo
    # listAsProbability = [(1.0/x)*100 for x in dati_db.keys()]
    # print sorted(listAsProbability,reverse=True)

    fig = pylab.gcf()
    fig.canvas.set_window_title("Vulnerability Curve")
    plt.grid(True)
    plt.title("Risk Curve using 6 Return Periods")
    plt.xlabel("Annual Probabilities %", color="red")
    plt.ylabel("Affected People", color="red")
    plt.tick_params(axis="x", labelcolor="b")
    plt.tick_params(axis="y", labelcolor="b")
    plt.plot(sorted(eccolo.keys(),reverse=False),eccolo.values(), 'ro--')
    for x, y in sorted(dati_db.iteritems(), reverse=False):
        plt.annotate(str(round(y, 2)), xy =(x,y), xytext=(5, 1), textcoords='offset points', color='red', size=8)
    plt.show()

admin = 154560
lista_valori = hazardIntensity_damageData(admin)
plotVulnerabilityCurve(lista_valori)
