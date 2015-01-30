__author__ = 'fabio.lana'

#Standard Modules
import collections
import matplotlib.pyplot as plt
import pylab
import numpy as np
import scipy.interpolate
import scipy.optimize
from scipy.interpolate import interp1d
from scipy import interpolate
import scipy.stats as stats

dati_per_plot = {}
dati_per_prob = {}

def plot_affected(people_rp, admin):

    titolofinestra = "People Living in Flood Prone Areas"

    # Plotting affected people
    affected_people = {}
    for row in people_rp:
        affected_people[row[0]] = row[1]

    affected_people_ordered = collections.OrderedDict(sorted(dict(affected_people).items()))

    fig = pylab.gcf()
    fig.canvas.set_window_title("Affected by RP")

    plt.grid(True)
    plt.title(admin)
    plt.xlabel("Return Periods")
    plt.ylabel("People in Flood Prone Area")
    plt.bar(range(len(affected_people_ordered)), affected_people_ordered.values(), align='center')
    plt.xticks(range(len(affected_people_ordered)), affected_people_ordered.keys())
    plt.show()

    return affected_people,affected_people_ordered

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

    # interpolate with piecewise constant function (p =0)
    y0 = scipy.interpolate.interp1d(x, y, kind='nearest')

    # interpolate with piecewise linear func (p =1)
    y1 = scipy.interpolate.interp1d(x, y, kind='linear')

    plt.grid(True)
    pylab.plot(x, y, 'o', label='Affected People')
    pylab.plot(xfine, y0(xfine), label='nearest')
    pylab.plot(xfine, y1(xfine), label='linear')

    pylab.legend()
    pylab.xlabel('x')

    #pylab.savefig('interpolate.pdf')
    pylab.show()

def interpolazione_tempi_ritorno_intermedi(dati_per_prob):

    dict_data = dict(dati_per_prob)
    dict_data_new = dict_data.copy()

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

    print ordinato_new
    data_prob = {}
    for giratore in ordinato_new.iterkeys():
        data_prob[(1.0/giratore)*100] = int(ordinato_new[giratore])

    print data_prob

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

p_rp = [(25, 1964.06536698), (50, 1532.03160453), (100, 9053.56506145), (200, 16710.9509999), (500, 1819.66620421), (1000, 153.189771891)]
#dct_p_rp = plot_affected(p_rp,"Test")
#dat_prob_plot = plot_risk_curve(dct_p_rp[1])
#plot_risk_interpolation(dat_prob_plot[0])
#rp_intermedi = interpolazione_tempi_ritorno_intermedi(dat_prob_plot[1])
#plot_risk_interpolation_linear(rp_intermedi[1])
#plot_risk_interpolation_linear_non_girato(rp_intermedi[1])

x = [1964, 3496, 12549, 29260, 31080, 31233]
y = [4.0, 2.0, 1.0, 0.5, 0.2, 0.1]
#y = [0.1, 0.2, 0.4, 1.0, 2.0, 4.0]
#y = [1000.0, 500.0, 200.0, 100.0, 50.0, 25.0]
#y = [25,50,100,200,500,1000]
y_norm = []
for val in y:
    y_corr = (val-min(y))/(max(y)-min(y))
    y_norm.append(y_corr)
print y_norm

f = interpolate.interp1d(x, y)

xnew = np.arange(min(x), max(x), 1000)
#print xnew

ynew = f(xnew) #use interpolation function returned by `interp1d`
plt.plot(x, y, 'o', xnew, ynew, 'r--')
plt.show()

from scipy.integrate import simps, trapz
# Compute the area using the composite trapezoidal rule.
area = trapz(y, x=[6000,15000], dx=1)
print("area = %.2f perc=%.2f " % (area, area/100))

# Compute the area using the composite Simpson's rule.
area = simps(y, dx=1)
print("area = %.2f perc=%.2f " % (area, area/100))
