__author__ = 'fabio.lana'

#Standard Modules
import collections
import matplotlib.pyplot as plt
import pylab
import numpy as np
import scipy as sp
from scipy import stats as st
from scipy.optimize import curve_fit
from scipy.integrate import trapz
import pandas as pd

dati_prob = {}
dati_prob_perc = {}

def ordina_dati(persone_tempi_di_ritorno):

    x = []
    y = []
    y_cum = []
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
        dizio_valori[x_corr] = y_corr, valore
    return dizio_valori, x, y, y_cum

def plot_affected(people_rp):

    #print people_rp
    titolofinestra = "People Living in Flood Prone Areas"

    # Plotting affected people
    affected_people = {}
    for rp, persone in people_rp.iteritems():
        affected_people[rp] = persone

    affected_people_ordered = collections.OrderedDict(sorted(dict(affected_people).items()))

    fig = pylab.gcf()
    fig.canvas.set_window_title("Affected by RP")

    plt.grid(True)
    plt.xlabel("Return Periods")
    plt.ylabel("People in Flood Prone Area")
    plt.bar(range(len(affected_people_ordered)), affected_people_ordered.values(), align='center')
    plt.xticks(range(len(affected_people_ordered)), affected_people_ordered.keys())
    plt.show()

    return affected_people, affected_people_ordered

def plot_risk_curve(dict_people_affected):

    pop_temp = 0
    for periodo, popolazione in sorted(dict_people_affected.iteritems()):
        annual_perc = 1/(periodo/100.0)
        pop_temp = pop_temp + popolazione
        dati_prob[annual_perc] = pop_temp

    fig = pylab.gcf()
    fig.canvas.set_window_title("Risk Curve")
    plt.grid(True)
    plt.title("Risk Curve Six Return Periods")
    plt.xlabel("Annual Probabilities %", color="red")
    plt.ylabel("Affected People", color="red")
    plt.tick_params(axis="x", labelcolor="b")
    plt.tick_params(axis="y", labelcolor="b")
    plt.plot(sorted(dati_prob.keys(), reverse=True), sorted(dati_prob.values(), reverse=False), 'ro--')
    for x, y in dati_prob.iteritems():
        plt.annotate(str(int(round(y, 2))), xy=(y, x), xytext=(5, 5), textcoords='offset points', color='red', size=8)
    plt.show()

    return dati_prob

def plot_risk_curve_tr(dict_people_affected):

    pop_temp = 0
    for periodo, popolazione in dict_people_affected.iteritems():
        pop_temp = pop_temp + popolazione
        dati_prob_perc[periodo] = popolazione

    fig = pylab.gcf()
    fig.canvas.set_window_title("Risk Curve")
    plt.grid(True)
    plt.title("Risk Curve using 6 Return Periods")
    plt.xlabel("Annual Probabilities %", color="red")
    plt.ylabel("Affected People", color="red")
    plt.tick_params(axis="x", labelcolor="r")
    plt.tick_params(axis="y", labelcolor="r")
    x = sorted(dati_prob_perc.keys(), reverse = False)
    y = sorted(dati_prob_perc.values())
    plt.plot(x, y, 'ro--')
    for x, y in dati_prob_perc.iteritems():
        plt.annotate(str(int(round(y, 2))), xy=(x, y), xytext=(5, 5), textcoords='offset points', color='red', size=8)
    plt.show()

    return dati_prob_perc

def calcolo_aree_grafici(dati_per_plot):

    x, y = dati_per_plot.keys(), dati_per_plot.values()

    # Compute the area using the composite trapezoidal rule
    area = trapz(y, x=[1964, 31233], dx=1)
    print("area trapezi= %.2f " % area)

    #area1 = trapz(y)
    #print("area = %.2f " % area1)

def curve_fitting_r2(dict_people_affected):

    def func(x, a, b, c):
        return a * np.exp(-b * x) + c

    #x = np.linspace(0,4,50)
    x = dict_people_affected
    #y = func(x, 2.5, 1.3, 0.5)
    y = func(x)
    yn = y + 0.2 * np.random.normal(size=len(x))

    popt, pcov = curve_fit(func, x, yn)

    print "Mean Squared Error: ", np.mean((y-func(x, *popt))**2)
    ss_res = np.dot((yn - func(x, *popt)), (yn - func(x, *popt)))
    ymean = np.mean(yn)
    ss_tot = np.dot((yn-ymean),(yn-ymean))
    print "Mean R :",  1-ss_res/ss_tot

    plt.figure()
    plt.plot(x, yn, 'ko', label="Original Noised Data")
    plt.plot(x, func(x, *popt), 'r-', label="Fitted Curve")
    plt.legend()
    plt.show()

def dizionario_to_pandas(dizio_valori_passato):

    df_flood = pd.DataFrame(dizio_valori_passato, index=['single', 'cumulated'])
    means = df_flood.mean(axis=1)
    stds = df_flood.std(axis=1)
    medians = df_flood.median(axis=1)
    mins = df_flood.min(axis=1)
    maxs = df_flood.max(axis=1)
    min_cal = mins['cumulated']
    max_cal = maxs['cumulated']
    mean_cal = means['cumulated']
    sd_cal = stds['cumulated']
    return min_cal, max_cal, mean_cal, sd_cal

def discrete(xk,pk):

    xk = np.arange(6)
    pk = (4, 2, 1, 0.5, 0.2, 0.1)

    custm = st.rv_discrete(name='custm', values=(xk, pk))
    fig, ax = plt.subplots(1, 1)
    ax.plot(xk, custm.pmf(xk), 'ro', ms=12, mec='r')
    ax.vlines(xk, 0, custm.pmf(xk), colors='r', lw=4)
    plt.show()

p_rp = [(25, 1964), (50, 1532), (100, 9053), (200, 16710), (500, 1819), (1000, 153)]
dizio_valori = ordina_dati(p_rp)

#pos[0] dizionario ; pos[1] tr ; pos[2] pop_tr;pos[3] pop_cumulata
tr = dizio_valori[1]
pop_tr = dizio_valori[2]
pop_cum = dizio_valori[3]

#plot_affected(dict(zip(tr, pop_tr)))
#plot_affected(dict(zip(tr, pop_cum)))
#plot_risk_curve(dict(zip(tr, pop_tr)))
rp_cumulati = dict(zip(tr, pop_cum))
dat_prob_plot_perc = plot_risk_curve_tr(rp_cumulati)
calcolo_aree_grafici(dat_prob_plot_perc)
#print dizionario_to_pandas(dizio_valori)
#curve_fitting_r2(rp_cumulati)
#discrete(pop_cum, tr)