__author__ = 'fabio.lana'
import scipy as sp
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt

from scipy import stats
s = sp.randn(100)

print("Standard Deviation: {0:8.6f}".format(s.std()))

n, min_max, mean, var, skew, kurt = stats.describe(s)
print("Number of elements: {0:d}".format(n))
print("Minimum: {0:8.6f} Maximum: {1:8.6f}".format(min_max[0], min_max[1]))
print("Mean: {0:8.6f}".format(mean))
print("Variance: {0:8.6f}".format(var))
print("Skew : {0:8.6f}".format(skew))
print("Kurtosis: {0:8.6f}".format(kurt))

#mean = 3.5 and standard deviation = 2.0
n = stats.norm(loc=3.5, scale=2.0)
print("Random number for the Gaussian distribution calculated %.4f" % (n.rvs()))

#The value of the PDF at any value of the variate can be
# obtained using the function pdf of the concerned distribution.
# .
val_0 = stats.norm.pdf(0, loc=0.0, scale=1.0)
print("PDF of Gaussian of mean = 0.0 and std. deviation = 1.0 at 0 is equals to %.4f" % (val_0))

#PASSANDO UN ARRAY DI VALORI
print(stats.norm.pdf([-0.1, 0.0, 0.1], loc=0.0, scale=1.0))

tries = range(11) # 0 to 10
print(stats.binom.pmf(tries, 10, 0.5))

def binom_pmf(n=4, p=0.5):
    # There are n+1 possible number of "successes": 0 to n.
    x = range(n+1)
    y = stats.binom.pmf(x, n, p)
    plt.plot(x,y,"o", color="black")

    # Format x-axis and y-axis.
    plt.axis([-(max(x)-min(x))*0.05, max(x)*1.05, -0.01, max(y)*1.10])
    plt.xticks(x)
    plt.title("Binomial distribution PMF for tries = {0} & p ={1}".format(
            n,p))
    plt.xlabel("Variate")
    plt.ylabel("Probability")

    plt.draw()
    plt.show()

binom_pmf()

#lavorando con CDF CUMULATIVE DENSITY FUNCTION
print(stats.norm.cdf(0.0, loc=0.0, scale=1.0))

def norm_cdf(mean=0.0, std=1.0):

    # 50 numbers between -3sd and 3sd
    x = sp.linspace(-3*std, 3*std, 50)

    # CDF at these values
    y = stats.norm.cdf(x, loc=mean, scale=std)

    plt.plot(x,y, color="black")
    plt.xlabel("Variate")
    plt.ylabel("Cumulative Probability")
    plt.title("CDF for Gaussian of mean = {0} & std. deviation = {1}".format(mean, std))
    plt.draw()
    plt.show()

norm_cdf()