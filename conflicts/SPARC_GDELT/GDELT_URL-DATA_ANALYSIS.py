__author__ = 'fabio.lana'

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine

def gdelt_pandas_date(returned_df):

    mindata = returned_df['SQLDATE'].min()
    maxdata = returned_df['SQLDATE'].max()

    returned_df['Date'] = pd.Series([pd.to_datetime(date) for date in returned_df['SQLDATE']], index= returned_df.index)
    print returned_df.head()

    bymonth = returned_df.groupby('Date')
    bygroup_type = returned_df.groupby(['Date', 'ActionGeo_Type'])
    print(bygroup_type.describe())

def analizziamo_dati_storici(nome_tabella):

    engine = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports')
    connection = engine.connect()
    returned_df = pd.DataFrame(pd.io.sql.read_sql_table(nome_tabella, engine, schema='conflicts', index_col='day'))
    returned_df['Date'] = pd.Series([pd.to_datetime(date) for date in returned_df.index], index= returned_df.index)
    returned_df['Year'] = pd.DatetimeIndex(returned_df['Date']).year
    returned_df['Month'] = pd.DatetimeIndex(returned_df['Date']).month
    returned_df['Day'] = pd.DatetimeIndex(returned_df['Date']).day

    connection.close()

    return returned_df

def main():
    paese = 'kyrgyzstan'
    #paese = 'southsudan'
    valore_tempo = "_historical"
    tabella = 'gd_' + paese + valore_tempo
    print tabella

    ritornati = analizziamo_dati_storici(tabella)
    df = pd.DataFrame(ritornati)

    # print(df.values[2])
    # print(df[['Month','GoldsteinScale']]['20000104':'20010104'])
    # print(df.ix[[0, 2], 4:10])

    eventi_by_category = df.groupby('QuadCategory')
    df_ilgruppo4 = eventi_by_category.get_group('4')
    #print df_ilgruppo4
    df_ilgruppo4_valori = eventi_by_category.get_group('4').values
    print df_ilgruppo4.describe()

    metriche = pd.DataFrame(eventi_by_category.describe())
    #metriche.to_csv("metriche.csv")

    pivot = pd.pivot_table(ritornati, values="Day", index=["Year", "Month"], columns=["QuadCategory"], aggfunc=len)
    pivot = pivot.fillna(0) # Replace any missing data with zeros
    pivot = pivot.reset_index()
    #print pivot
    # date-generating function:
    get_date = lambda x: dt.datetime(year=int(x[0]), month=int(x[1]), day=1)

    pivot["date"] = pivot.apply(get_date, axis=1) # Apply row-wise
    pivot = pivot.set_index("date") # Set the new date column as the index

    # Now we no longer need the Year and Month columns, so let's drop them:
    pivot = pivot[["1", "2", "3", "4"]]
    # Rename the QuadCat columns
    pivot = pivot.rename(columns={"1": "Material Cooperation",
                                  "2": "Verbal Cooperation",
                                  "3": "Verbal Conflict",
                                  "4": "Material Conflict"})
    
    #pivot["Material Conflict"].plot(figsize=(12, 6))
    #pivot.plot(figsize=(12, 6))
    #plt.show()

if __name__ == "__main__":
    main()

