__author__ = 'fabio.lana'

#Standard Modules
import collections
import matplotlib.pyplot as plt
import pylab
import numpy as np
import scipy.stats as sta
import scipy.interpolate
import scipy.optimize
from scipy.interpolate import interp1d, splrep, splev
from scipy.optimize import curve_fit
from scipy.integrate import simps, trapz
import pandas as pd
import math

dati_per_plot = {}
dati_per_prob = {}

def plot_affected(people_rp):

    titolofinestra = "People Living in Flood Prone Areas"

    # Plotting affected people
    affected_people = {}
    for rp, persone in people_rp.iteritems():
        #print rp, persone[0]
        affected_people[rp] = persone[0]

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
    for periodo in dict_people_affected.iteritems():
        annual_perc = 1/(periodo[0]/100.0)
        pop_temp = pop_temp + periodo[1]
        dati_per_plot[annual_perc] = pop_temp
        dati_per_prob[periodo[0]] = pop_temp

    fig = pylab.gcf()
    fig.canvas.set_window_title("Risk Curve")
    plt.grid(True)
    plt.title("Risk Curve using 6 Return Periods")
    plt.xlabel("Affected People", color="red")
    plt.ylabel("Annual Probabilities %", color="red")
    plt.tick_params(axis="x", labelcolor="b")
    plt.tick_params(axis="y", labelcolor="b")
    plt.plot(sorted(dati_per_plot.values(), reverse=True), sorted(dati_per_plot.keys()), 'ro--')
    for x, y in dati_per_plot.iteritems():
        plt.annotate(str(int(round(y, 2))), xy=(y, x), xytext=(5, 5), textcoords='offset points', color='red', size=8)
    plt.show()

    return dati_per_plot,dati_per_prob

def plot_risk_interpolation(dati_per_plot):

    x, y = dati_per_plot.keys(), dati_per_plot.values()

    # use finer and regular mesh for plot
    xfine = np.linspace(0.1, 4, 25)

    # interpolations
    y0 = scipy.interpolate.interp1d(x, y, kind='nearest')
    y1 = scipy.interpolate.interp1d(x, y, kind='linear')
    y2 = scipy.interpolate.interp1d(x, y, kind='cubic')

    plt.grid(True)
    pylab.plot(x, y, 'o', label='Affected People')
    pylab.plot(xfine, y0(xfine), label='nearest')
    pylab.plot(xfine, y1(xfine), label='linear')
    pylab.plot(xfine, y2(xfine), label='cubic')

    pylab.legend()
    pylab.xlabel('x')

    #pylab.savefig('interpolate.pdf')
    pylab.show()

def interpolazione_tempi_ritorno_intermedi(dati_per_prob):

    dict_data = dict(dati_per_prob)
    dict_data_new = dict_data.copy()
    dict_pop_new = dict_data.copy()

    xdata = dict_data.keys()
    ydata = dict_data.values()

    f = interp1d(xdata, ydata)

    nuovi_RP = [75, 150, 250, 750]
    for xnew in nuovi_RP:
        popolazione_interpolata = f(xnew)
        dict_data_new[xnew] = float(popolazione_interpolata)

    ordinato_old = collections.OrderedDict(sorted(dict(dict_data).items()))
    ordinato_new = collections.OrderedDict(sorted(dict(dict_data_new).items()))

    return ordinato_old, ordinato_new

def plot_risk_interpolation_linear(ordinato_new):

    data_prob = {}
    for giratore in ordinato_new.iterkeys():
        data_prob[(1.0/giratore)*100] = ordinato_new[giratore]

    titolo_plot = "Risk Curve using RP 25,50,75,100,150,200,500,750 and 1000 Years"
    x, y = data_prob.keys(), data_prob.values()
    xfine = np.linspace(0.1, 4, 25)
    y1 = scipy.interpolate.interp1d(x, y, kind='linear')
    plt.grid(True)

    fig = pylab.gcf()
    fig.canvas.set_window_title(titolo_plot)
    plt.grid(True)
    plt.title("Test")

    pylab.plot(x, y, 'o', label='Affected People')
    pylab.plot(xfine, y1(xfine), label='linear')

    for x, y in data_prob.iteritems():
        plt.annotate(str(int(round(y, 2))), xy=(y,x), xytext=(5,5), textcoords='offset points', color='red', size=8)

    pylab.legend()
    pylab.xlabel('x')
    #pylab.savefig('interpolate.pdf')
    pylab.show()

def plot_risk_interpolation_linear_non_girato(ordinato_new):

    data_prob = {}
    for giratore in ordinato_new.iterkeys():
        data_prob[(1.0/giratore)*100] = int(ordinato_new[giratore])

    titolo_plot = "Risk Curve using RP 25,50,75,100,150,200,500,750 and 1000 Years"
    x, y = data_prob.keys(), data_prob.values()

    xfine = np.linspace(0.1, 4, 25)
    y1 = scipy.interpolate.interp1d(x, y, kind='linear')
    plt.grid(True)

    fig = pylab.gcf()
    fig.canvas.set_window_title(titolo_plot)
    plt.grid(True)
    plt.title("Test")

    pylab.plot(y, x, 'o', label='Affected People')
    pylab.plot(y1(xfine), xfine, label='linear')

    for x, y in data_prob.iteritems():
        plt.annotate(str(int(round(y, 2))), xy=(y, x), xytext=(5, 5), textcoords='offset points', color='red', size=8)

    pylab.legend()
    pylab.xlabel('x')
    #pylab.savefig('interpolate.pdf')
    pylab.show()

def calcolo_aree_grafici(dati_per_plot):

    x, y = dati_per_plot.keys(), dati_per_plot.values()

    # Compute the area using the composite trapezoidal rule.
    area = trapz(y, x=[1964, 31233], dx=1)
    print("area = %.2f " % (area))

    area1 = trapz(x)
    print("area = %.2f " % (area1))
    # Compute the area using the composite Simpson's rule.

    area2 = simps(y, dx=1)
    print("area = %.2f " % (area2))

def normalizzatore(y):

    valori_passati = sorted(y)
    y_norm = []
    for val in valori_passati:
        y_corr = (val - min(y)) / float((max(y) - min(y)))
        y_norm.append(y_corr)
    print y_norm

def curve_fitting_r2():

    def func(x, a, b, c):
        return a * np.exp(-b * x) + c

    x = np.linspace(0,4,50)
    y = func(x, 2.5, 1.3, 0.5)
    yn = y + 0.2*np.random.normal(size=len(x))

    popt, pcov = curve_fit(func, x, yn)

    print "Mean Squared Error: ", np.mean((y-func(x, *popt))**2)
    ss_res = np.dot((yn - func(x, *popt)),(yn - func(x, *popt)))
    ymean = np.mean(yn)
    ss_tot = np.dot((yn-ymean),(yn-ymean))
    print "Mean R :",  1-ss_res/ss_tot

    plt.figure()
    plt.plot(x, yn, 'ko', label="Original Noised Data")
    plt.plot(x, func(x, *popt), 'r-', label="Fitted Curve")
    plt.legend()
    plt.show()

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
    return dizio_valori

def normpdf(x, mean, sd):
    var = float(sd)**2
    pi = 3.1415926
    denom = (2*pi*var)**.5
    num = math.exp(-(float(x)-float(mean))**2/(2*var))
    return num/denom

def dizionario_to_pandas():

    df_flood = pd.DataFrame(dizio_valori, index=['single', 'cumulated'])
    means = df_flood.mean(axis=1)
    stds = df_flood.std(axis=1)
    medians = df_flood.median(axis=1)
    mean_cal = means['cumulated']
    sd_cal = stds['cumulated']

def calcolo_pdf_manuale(dizio_e_caio):

    calcoli = []
    for illo in dizio_e_caio.iteritems():
        come = illo[1][0]
        tornato = normpdf(come, mean_cal, sd_cal)
        calcoli.append(tornato)
    print calcoli
    plt.plot(sorted(calcoli))
    plt.show()

p_rp = [(25, 1964), (50, 1532), (100, 9053), (200, 16710), (500, 1819), (1000, 153)]
dizio_valori = ordina_dati(p_rp)
dizionario_to_pandas()
#calcolo_pdf_manuale(dizio_valori)
dct_p_rp = plot_affected(dizio_valori)
dat_prob_plot = plot_risk_curve(dct_p_rp[1])
plot_risk_interpolation(dat_prob_plot[0])
rp_intermedi = interpolazione_tempi_ritorno_intermedi(dat_prob_plot[1])
plot_risk_interpolation_linear(rp_intermedi[1])
plot_risk_interpolation_linear_non_girato(rp_intermedi[1])
calcolo_aree_grafici(dat_prob_plot[1])
#normalizzatore(y)
#curve_fitting_r2()