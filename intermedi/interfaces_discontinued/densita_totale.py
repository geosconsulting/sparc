__author__ = 'fabio.lana'

from sqlalchemy import create_engine, MetaData
import pandas as pd
import os
from osgeo import ogr

def crea_connessione():

    engine = create_engine(r'postgresql://geonode:geonode@127.0.0.1/geonode-imports')
    metadata = MetaData(engine, schema='public')

    try:
        conn = engine.connect()
        conn.execute("SET search_path TO public")
    except Exception as e:
        print e.message

    return engine, conn

def lettura_tabelle_e_merge(engine):

    tbl_rp_name = 'sparc_adm2_population_rp'
    tbl_pop_name = 'sparc_adm2_area_population'
    df_rp = pd.read_sql_table(tbl_rp_name, engine, index_col='index')
    df_pop = pd.read_sql_table(tbl_pop_name, engine, index_col='index')
    df_tot = pd.merge(df_pop, df_rp, on='adm2_code', how='outer')

    return df_tot

def calcolo_densita_percentuali(df_tot):

    area_val = df_tot['area_sqkm_x']
    pop_val = df_tot['pop']
    df_tot['density'] = pop_val / area_val
    df_tot['perc_25'] = df_tot['rp25'] / pop_val * 100
    df_tot['perc_50'] = df_tot['rp50'] / pop_val * 100
    df_tot['perc_100'] = df_tot['rp100'] / pop_val * 100
    df_tot['perc_200'] = df_tot['rp200'] / pop_val * 100
    df_tot['perc_500'] = df_tot['rp500'] / pop_val * 100
    df_tot['perc_1000'] = df_tot['rp1000'] / pop_val * 100
    df_tot['dens_25'] = df_tot['rp25'] / area_val
    df_tot['dens_50'] = df_tot['rp50'] / area_val
    df_tot['dens_100'] = df_tot['rp100'] / area_val
    df_tot['dens_200'] = df_tot['rp200'] / area_val
    df_tot['dens_500'] = df_tot['rp500'] / area_val
    df_tot['dens_1000'] = df_tot['rp1000'] / area_val

    return df_tot

def classazione_valori(df_tot):

    valori = df_tot['density'].describe()
    limiti = int(valori[4]),int(valori[5]),int(valori[6]),int(valori[7])

    valori_perc = df_tot['perc_25'].describe()
    limiti_perc = int(valori_perc[4]),int(valori_perc[5]),int(valori_perc[6]), int(valori_perc[7])

    def ordinal_classification(colonna):

        if colonna < limiti[0]:
            return 'low'
        elif colonna > limiti[0] and colonna < limiti[1]:
            return 'medium'
        elif colonna > limiti[1] and colonna < limiti[2]:
            return 'high'
        else:
            return 'very high'

    def percent_classification(colonna_perc):

        if colonna_perc < limiti_perc[0]:
            return 'low'
        elif colonna_perc > limiti_perc[0] and colonna_perc < limiti_perc[1]:
            return 'medium'
        elif colonna_perc > limiti_perc[1] and colonna_perc < limiti_perc[2]:
            return 'high'
        else:
            return 'very high'

    df_dens_pop = pd.DataFrame({'dens_pop': df_tot['density'].apply(ordinal_classification)})
    df_dens_pop_25RP = pd.DataFrame({'dens_pop_rp25': df_tot['perc_25'].apply(percent_classification)})
    ddd = df_dens_pop.combine_first(df_dens_pop_25RP)
    print ddd.head()

def lettura_tabella_densita(engine):

    tbl_sparc_adm2_density = 'sparc_adm2_density'
    df_dens = pd.read_sql_table(tbl_sparc_adm2_density, engine, index_col='index')

    return df_dens

def lettura_tabella_probabilita_mensili(engine):

    tbl_sparc_month_prec_norm = 'sparc_month_prec_norm'
    df_montlhy_prob = pd.read_sql_table(tbl_sparc_month_prec_norm, engine, index_col='id')

    return df_montlhy_prob

def lettura_tabelle_pgis():

    databaseServer = "127.0.0.1"
    databaseName = "geonode-imports"
    databaseUser = "geonode"
    databasePW = "geonode"

    connString = "PG: host=%s dbname=%s user=%s password=%s " %(databaseServer,databaseName,databaseUser,databasePW)
    conn = ogr.Open(connString)

    layerList = []
    for i in conn:
        daLayer = i.GetName()
        if not daLayer in layerList:
            layerList.append(daLayer)

    layerList.sort()

    for j in layerList:
        print j

    conn.Destroy()

engine, conn = crea_connessione()

il_paese = 'Cameroon'

##TUTTI I PEZZI DI CODICE PER SCRIVERE LE TABELLE NEL DB
#tabella_totale = lettura_tabelle_e_merge(engine)
#tabellone_con_densita = calcolo_densita_percentuali(tabella_totale)
#tabellone_con_densita.fillna(value=0.0)
#La classazione la faro' direttamente da Python cosi vedo come farla al meglio
#classazione_valori(tabella_totale)
#table_adm2_density = 'sparc_adm2_density'
#tabellone_con_densita.to_sql(table_adm2_density, engine, schema='public')

tabella_densita_annuali = lettura_tabella_densita(engine)
tabella_probabilita_mensili = lettura_tabella_probabilita_mensili(engine)

table_cameroon = tabella_densita_annuali[tabella_densita_annuali['adm0_name'] == il_paese]
table_per_adm1 = table_cameroon.groupby(['adm1_name'])

#print table_per_adm1.pop.sum()

# for nome in table_per_adm1.adm2_name_x:
#     print nome

# temp1 = table_per_adm1.pop.count()
# temp2 = table_per_adm1.pop.sum() / table_per_adm1.hectares.sum()
# fig1 = plt.figure(figsize=(12,6))
#
# ax1 = fig1.add_subplot(121)
# ax1.set_xlabel('Adm Level 1')
# ax1.set_ylabel('Population')
# ax1.set_title('Population By Admin 1 in Cameroon')
# temp1.plot(kind='bar')
#
# ax2 = fig1.add_subplot(122)
# temp2.plot(kind='bar')
# ax2.set_xlabel('Admin 1')
# ax2.set_ylabel('Density per Hectare')
# ax2.set_title('Population Density By Admin 1 in Cameroon')
# plt.show()

##BOXPLOT DEI DATI DI DENSITA
#table_per_adm1.boxplot(column='density')
#table_per_adm1.boxplot(column='density', by= ['adm2_name_x'])
#plt.show()

lettura_tabelle_pgis()