__author__ = 'fabio.lana'
from scipy.stats import norm
import numpy as np
import pylab as plt

x = np.arange(-4,4,0.01)

plt.show(x,norm().pdf(x))
