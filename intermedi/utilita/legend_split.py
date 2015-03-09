__author__ = 'fabio.lana'

arrAnn = [('5890', 7, 0, 0, 0, 0, 0),
          ('5909', 161, 13, 21, 104, 2, 0),
          ('5921', 528, 3, 0, 0, 0, 0),
          ('5901', 5, 0, 3, 3, 0, 0),
          ('5926', 15, 0, 0, 0, 0, 0),
          ('5936', 102, 1, 2, 1, 2, 1),
          ('5893', 13, 0, 0, 0, 0, 0),
          ('5888', 1, 0, 0, 0, 0, 0),
          ('5900', 48, 0, 2, 2, 2, 0),
          ('5904', 17, 0, 0, 0, 0, 0),
          ('5916', 147, 63, 48, 3, 0, 2),
          ('5879', 102, 1, 0, 0, 10, 1),
          ('5915', 31, 0, 2, 0, 70, 0),
          ('5933', 44, 0, 0, 1, 0, 0),
          ('5873', 7, 0, 0, 0, 0, 0),
          ('5896', 132, 0, 0, 0, 1, 1)]

def connessione_sqlalchemy():

    from sqlalchemy import create_engine, Table, MetaData

    engine = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports')
    connection = engine.connect()
    metadata = MetaData(engine)
    #connection.execute("SET search_path TO test")
    tab_paesi = Table('sparc_population_month', metadata, autoload=True,  autoload_with=connection, postgresql_ignore_search_path=True)
    connection.close()

    s = tab_paesi.select()
    rs = s.execute()
    paesi_dal_db = rs.fetchall()

    paesi = []
    for paese in paesi_dal_db:
        #paesi.append(paese[0])
        print paese

host = 'localhost'
schema = 'public'
dbname = 'geonode-imports'
user = 'geonode'
password = 'geonode'

import psycopg2

def apri_connessione():

    connection_string = "dbname=%s user=%s password=%s host=%s" % (dbname, user, password, host)
    try:
        db_connessione = psycopg2.connect(connection_string)
        db_cursore = db_connessione.cursor()
        #print("Connessione attiva")
    except:
        print("No connection")

    return db_connessione,db_cursore

def gather_data(db_cursore,paese):

    sql_annual = "SELECT adm2_code,rp25,rp50,rp100,rp200,rp500,rp1000 FROM sparc_annual_pop WHERE adm0_name = '" + paese + "';"
    db_cursore.execute(sql_annual);
    adm2_by_country__annual = db_cursore.fetchall()

    sql_monthly = "SELECT * FROM sparc_population_month WHERE adm0_name = '" + paese + "' ORDER BY adm2_code;"
    db_cursore.execute(sql_monthly);
    adm2_by_country__monthly = db_cursore.fetchall()

    #res_noSpace = [str(x[0]).strip() for x in risultati]
    #res_val = risultati[1:]
    #tot = res_noSpace + res_val

    return adm2_by_country__annual, adm2_by_country__monthly

def chiudi_connessione(db_cursore,db_connessione):

    try:
        db_cursore.close()
        db_connessione.close()
        #print("Connessione chiusa")
    except:
        print "Problem in closing the connection"

paese = 'Bolivia'
conn, cur = apri_connessione()
array_values = gather_data(cur, paese)

maximo = 0
minimo = 0
tutte_somme = []
for vallo in array_values[0]:
#Array inventato
#for vallo in arrAnn:
    tramo = vallo[1:]
    tutte_somme.append(sum(tramo))

minimo = min(tutte_somme)
maximo = max(tutte_somme)

grandezza = (len(str(maximo)))
#print "La lunghezza dei caratteri e' %d" % (grandezza)

inizio = str(maximo)[1]
#print "Cifra Inizio %s " % inizio

divi_molti = int('1' + '0'*(grandezza-1))
#print "Divisore Moltiplicatore %s" % divi_molti

print paese
print "Min %d Max %d" % (minimo, maximo)

lower_treshold = 100
upper_treshold = divi_molti-(divi_molti/10)
print "Low %d High %d Thresholds" % (lower_treshold, upper_treshold)

less_than = minimo + lower_treshold
if upper_treshold>maximo:
    more_than = upper_treshold - maximo
else:
    more_than = maximo - upper_treshold

#interval = more_than - less_than
interval = maximo - minimo
print "Interval %d" % interval
tertile = interval/4
print "Tertile %d" % tertile

intermediate = []
for mover in range(1, 4):
    intermediate.append(tertile*mover)

print "Second split %d third split %d fourth split %d" % (intermediate[0],intermediate[1],intermediate[2])
print
print "LEGEND"
print "First class - Less than %d (calculated value %d)" % (lower_treshold,minimo)
print "Second class between %d and %d" % (less_than,intermediate[0])
print "Third class between %d and %d" % (intermediate[0],intermediate[1])
print "Fourth class between %d and %d" % (intermediate[1],intermediate[2])
print "Last class - More than %d (calculated value %d)" % (intermediate[2], maximo)
print