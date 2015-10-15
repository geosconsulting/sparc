import numpy as np
import collections
import matplotlib.pyplot as plt

import matplotlib
matplotlib.style.use('ggplot')

import pylab
import numpy as np
import scipy as sp
from scipy import stats as st
from scipy.optimize import curve_fit
from scipy.integrate import trapz
import pandas as pd
from scipy.integrate import simps

def ordina_dati(persone_tempi_di_ritorno):

    x = []
    y = []
    y_cum = []
    perc = []

    dizio_valori = {}
    valore = 0

    for indice in range(0, len(persone_tempi_di_ritorno)):
        x_corr = p_rp[indice][0]
        y_corr = p_rp[indice][1]
        valore_corr = (p_rp[indice][1])
        valore = valore + valore_corr
        x.append(x_corr)
        y.append(y_corr)
        y_cum.append(valore)
        perc.append(1.0/p_rp[indice][0])
        dizio_valori[x_corr] = y_corr, valore
    return dizio_valori, x, y, y_cum,perc

p_rp = [(25, 1964), (50, 1532), (100, 9053), (200, 16710), (500, 1819), (1000, 153)]
dizio_valori = ordina_dati(p_rp)

tr = dizio_valori[1]
pop_tr = dizio_valori[2]
pop_cum = dizio_valori[3]
perc = dizio_valori[4]

y = np.array(perc)
x = np.array(pop_cum)
print simps(y, x)

tutto_pandas = dict(zip(tr,zip(pop_tr,pop_cum)))
df_flood = pd.DataFrame(tutto_pandas, index=['single', 'cumulated'])

means = df_flood.mean(axis=1)
stds = df_flood.std(axis=1)
medians = df_flood.median(axis=1)
mins = df_flood.min(axis=1)
maxs = df_flood.max(axis=1)
min_cal = mins['cumulated']
max_cal = maxs['cumulated']
mean_cal = means['cumulated']
sd_cal = stds['cumulated']

df_flood.ix[1].plot(kind='bar')
plt.show()



