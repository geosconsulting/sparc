__author__ = 'fabio.lana'
import numpy as np
import pylab as plt
import scipy as sp
from scipy import stats
import win32api


scores = np.array([114, 100, 104, 89, 102, 91, 114, 114, 103, 105,108,
                      130, 120, 132, 111, 128, 118, 119, 86, 72, 111,
                      103, 74, 112, 107, 103, 98, 96, 112, 112, 93])

xmean = sp.mean(scores)
sigma = sp.std(scores)
n = sp.size(scores)
print xmean, xmean - 2.576*sigma /sp.sqrt(n), xmean + 2.576*sigma / sp.sqrt(n)

result = sp.stats.bayes_mvs(scores)
print result