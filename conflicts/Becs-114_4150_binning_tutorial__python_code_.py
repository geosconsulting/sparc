# Tutorial on binning, PDFs, CDFs, 1-CDFs and more
# ================================================
# 
# Introduction
# ------------
# In this course, we will need to plot various experimental probability distributions.
# As we are dealing with data, whose sparsity, and order of magnitudes may vary a lot,
# we have provided this tutorial to help you out producing appropriate visualizations of the data.
# 
# 
# **Discrete variables**: Probability *mass* functions (PMF)
# --------------------------------------------------------
# 
# The counterpart of a PDF for a discrete variable is a normal probability mass function (PMF) $P(v)$. Let us assume we have some random variable $v$ that can have only discrete values. If we assume, for simplicity, that our random variable $v$ can only take integer values. Then, the probabilities for obtaining different values of $v$ are described a probability mass function:
# 
# * Probability of observing some value between $x$ and $y$ (with $x$ and $y$ included) equals
# 	
#     $$\sum_{v=x}^y P(v)$$
#     
# * The probability mass function is also normalized to one:    
#     $$\sum_{i=-\infty}^\infty P(i) = 1$$
#     
#     
# **Continuous variables**: Probability *density* function (PDF)
# --------------------------------------------------------------
# 
# The counterpart of a PMF for a *continuous* random variable $v$ is its probability *density* function (PDF), denoted also typically by $P(v)$. For a probability density function $P(v)$ it holds:
# 
# * Probability of observing a value between $x$ and $y$ $(>x)$ equals
# 
# 	$$\int_x^y P(v) dv$$
#     
# * The distribution is normalized to one:
# 
#     $$\int_{-\infty}^{\infty} P(v) dv = 1$$
# 
# 
# **Example of a PDF denoted by f(x):**
# 
# <img src="pdf-cpf.png" alt="PDF and CDF" style="width:445px;height:228px">
# (Figure from: http://physics.mercer.edu/hpage/CSP/pdf-cpf.gif)
# 
# ($F(x)$ denotes the cumulative density function, more of that later) 
# 
# Note that PDFs can have values greater than 1!
# 
# **From now on in this tutorial, we mostly assume that we work with continuous random variables**
# 
# In other words, we assume that the elements of our data arise from a distribution that are continuously distributed.
# In practice these same methods can (usually) be used also when we are dealing with discretely distributed data, such as node degrees in a network.  

# Computing and plotting experimental PDFs:
# -----------------------------------------
# 
# Let us start by presenting narrowly and broadly distributed data with Python using the standard settings:

# In[2]:

import matplotlib.pyplot as plt

# this is only for this ipython notebook:


import numpy as np

# narrowly distributed data
rands = np.random.rand(10000)
# broadly distributed data
one_per_rands = 1./rands

fig = plt.figure(figsize=(12,6))
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

# basic histograms (see hist function below)
# work well with narrowly distributed data 
#
# option: normed = True
#     divides the counts by the total number of observations and by bin widths
#     to compute the probability _density_ function
#
################################################################################
# NOTE (!)                                                                     #
# With numpy.histogram, the option normed=True does not always work properly!  #
# (use option density=True there!)                                             #
# However, when using matplotlib (ax.hist) this bug is corrected!              #
################################################################################

pdf, bins, _ = ax1.hist(rands, normed=True, label="pdf, uniform")
ax1.legend()
print "If the histogram yields a probability distribution, the following values should equal 1:"
print np.sum(pdf*(bins[1:]-bins[:-1]))



pdf, bins, _ = ax2.hist(one_per_rands, normed=True, label='pdf, power-law')
ax2.legend()
print np.sum(pdf*(bins[1:]-bins[:-1])) # should equal 1"

print "Further tricks needed for seeing the actual shape of the distribution!"
print "The plot on the right-hand side does not show much! (Broadly distributed data!)"


# What about increasing the number of bins?
# -----------------------------------------

# In[3]:


fig = plt.figure(figsize=(12,6))
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

_ = ax1.hist(one_per_rands, 10, normed=True, label='PDF, power-law, 10 bins')
_ = ax2.hist(one_per_rands, 100, normed=True, label='PDF, power-law, 100 bins')
ax1.legend()
ax2.legend()

print "Increasing the number of bins does not really help out:"


# Solution: logarithmic bins:
# ---------------------------
# 
# Use logarithmic bins instead of linear!

# In[4]:

fig = plt.figure(figsize=(12,6))
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

_ = ax1.hist(one_per_rands, bins=100, normed=True, label='PDF, lin-lin, power-law, 100 bins')
ax1.legend()

# creating logaritmically spaced bins


print "Min and max:"
print np.min(one_per_rands), np.max(one_per_rands)


# create log bins: (by specifying the multiplier)
bins = [np.min(one_per_rands)]
cur_value = bins[0]
multiplier = 2.5
while cur_value < np.max(one_per_rands):
    cur_value = cur_value * multiplier
    bins.append(cur_value)
bins = np.array(bins)
# an alterante way, if one wants to just specify the 
# number of bins to be used:
# bins = np.logspace(np.log10(np.min(one_per_rands)), 
#                    np.log10(np.max(one_per_rands)), 
#                    num=10)

print "The created bins:"
print bins

bin_widths = bins[1:]-bins[0:-1]
print "Bin widths are increasing:"
print bin_widths
print "The bin width is multiplied always multiplied by a constant factor:"
print bin_widths[1]/bin_widths[0]
print bin_widths[2]/bin_widths[1]


_ = ax2.hist(one_per_rands, bins=bins, normed=True, label='PDF, log-log, power-law')
ax1.legend()
ax2.set_xscale('log')
ax2.set_yscale('log') 

# How does 1/x look like in the log-log scale?

# Requires some knowledge on how different distributions look on log-log scale
# but now we can see what happens in the tail as well!


# Let's see how different distributions look like with different x- and y-scales:
# -------------------------------------------------------------------------------

# In[5]:

from scipy.stats import lognorm, expon



# Trying out different broad distributions with linear and logarithmic PDFs:

n_points = 100000

# power law:
# slope = -2!
one_over_rands = 1/np.random.rand(n_points)
# http://en.wikipedia.org/wiki/Power_law

# exponential distribution
exps = expon.rvs(size=1000)
# http://en.wikipedia.org/wiki/Exponential_distribution

# lognormal (looks like a normal distribution in a log-log scale!)
lognorms = lognorm.rvs(1.0, size=1000)
# http://en.wikipedia.org/wiki/Log-normal_distribution

fig = plt.figure(figsize=(15,15))
fig.suptitle('Different broad distribution PDFs in lin-lin, log-log, and lin-log axes')
n_bins = 30

for i, (rands, name) in enumerate(zip([one_over_rands, exps, lognorms],
                                      ["power law", "exponential", "lognormal"])):
    # linear-linear scale
    ax = fig.add_subplot(4, 3, i+1)
    ax.hist(rands, n_bins, normed=True)
    ax.text(0.5,0.9, "PDF, lin-lin: " + name, transform=ax.transAxes)
    # log-log scale
    ax = fig.add_subplot(4, 3, i+4)
    bins = np.logspace(np.log10(np.min(rands)), np.log10(np.max(rands)), num=n_bins)
    ax.hist(rands, normed=True, bins=bins)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.text(0.5,0.9, "PDF, log-log: " + name, transform=ax.transAxes)
    # lin-log
    ax = fig.add_subplot(4, 3, i+7)
    bins = np.logspace(np.log10(np.min(rands)), np.log10(np.max(rands)), num=n_bins)
    ax.hist(rands, normed=True, bins=bins)
    ax.text(0.5,0.9, "PDF, log-lin: " + name, transform=ax.transAxes)
    ax.set_xscale('log')
    # log-lin
    ax = fig.add_subplot(4, 3, i+10)
    ax.hist(rands, normed=True, bins=n_bins)
    ax.text(0.5,0.9, "PDF, lin-log: " + name, transform=ax.transAxes)
    ax.set_yscale('log')
    
    
print "Distributions can look a lot different depending on the binning and axes scales!\n"
print "Note that PDFs can have a value over 1!"
print "(it is the bin_width*pdf which counts for the normalization)"



# Summary so far:
# ---------------
# 
# * Choose axes scales and bins according to the data! (no all-round solution exists)
# 
# * Choosing appropriate bins can be difficult! 
# 
# * One way for getting around binning is to plot the cumulative density functions!
# 

# Cumulative density function (CDF(x)):
# -------------------------------------
# 
# * The **standard** mathematical definitions:
# 
# * Discrete variable:
#     $CDF(x) = \sum_{i \leq x} P(x)$
# 
# * Continuous variable:
#     $CDF(x) = \int_{-\infty}^{x} P(x') dx$
#     
# 
# * Sometimes **complementary cumulative distributions** are more practical (1-CDF(x) or ccdf). Useful especially with broadly distributed data (surprise) and when interested in the *tail* of the distribution.
# 
# * Discrete variable:
#     $1-CDF(x) = \sum_{i>x} P(x)$
# 
# * Continuous variable:
#     $1-CDF(x) = \int_{x}^{\infty} P(x') dx$
# 
# * Benefit of using CDF or 1-CDF: **no need for binning!**
# 
# 
# * **Note:** 
# 
# 
# * **For presenting experimental 1-CDFs** it is practical to use a bit different definition of the 1-CDF by including also the equality. The reason for this is that when plotting the 1-CDF on logarithmic y-scale, the last data point would not otherwise show up!
# 
# * So given some data vector $d$ data, we plot the experimental 1-CDFs as:
#     $$1-CDF(x) = \frac{\text{number of elements in $d$ that are $\geq x$}}{\text{number of elements in $d$}}$$
# 
# 
# 

# In[6]:

def plot_ccdf(data, ax):
    """
    Plot the complementary cumulative distribution function (1-CDF(x))
    based on the data on the axes object.
    
    Note that this way of computing and plotting the ccdf is not
    the best approach for a discrete variable, where many
    observations can have exactly same value!
    """
    # Note that, here we use the convention for presenting an 
    # experimental 1-CDF (ccdf) as discussed   
    # a quick way of computing a ccdf (valid for continuous data):
    sorted_vals = np.sort(data)
    # corresponding 1-CDF values from "1 to 1./len(data)"
    ccdf = np.linspace(1,1./len(data), len(data))
    ax.plot(sorted_vals, ccdf, "-")

    
def plot_cdf(data, ax):
    """
    Plot CDF(x) on the axes object
    
    Note that this way of computing and plotting the CDF is not
    the best approach for a discrete variable, where many
    observations can have exactly same value!
    """
    sorted_vals = np.sort(data)
    # now probs run from "0 to 1"
    probs = np.linspace(1./len(data),1, len(data))
    ax.plot(sorted_vals, probs, "-")


fig = plt.figure(figsize=(15,15))
fig.suptitle('Different broad distribution CDFs in lin-lin, log-log, and lin-log axes')
# loop over different experimental data distributions
# enumerate, enumerates the list elements (gives out i in addition to the data)
# zip([1,2],[a,b]) returns [[1,"a"], [2,"b"]]
for i, (rands, name) in enumerate(zip([one_over_rands, exps, lognorms],
                                      ["power law", "exponential", "lognormal"])):
    # linear-linear scale
    ax = fig.add_subplot(4,3,i+1)
    plot_cdf(rands, ax)
    ax.grid()
    ax.text(0.6,0.9, "lin-lin, CDF: " + name, transform=ax.transAxes)
    
    # log-log scale
    ax = fig.add_subplot(4,3,i+4)
    plot_cdf(rands, ax)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid()
    ax.text(0.6,0.9, "log-log, CDF: " + name, transform=ax.transAxes)

    # lin-lin 1-CDF
    ax = fig.add_subplot(4,3,i+7)
    plot_ccdf(rands, ax)
    ax.text(0.6,0.9, "lin-lin, 1-CDF: " + name, transform=ax.transAxes)
    ax.grid()
    
    # log-log 1-CDF
    ax = fig.add_subplot(4,3,i+10)
    plot_ccdf(rands, ax)
    ax.text(0.6,0.9, "log-log: 1-CDF " + name, transform=ax.transAxes)
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.grid()
    


# Notes
# -----
# 
# 
# - ** Only with 1-CDF one can zoom in to the tail **
# 
# - ** Sometimes lin-scale good, sometimes log sacle ** 
# 
# - ** Note that for power laws, PDF, and 1-CDF are both straight lines in log-log coordinates **
# 

# Plotting 2D-distributions
# -------------------------
# 
# What is the dependence between values of vectors X and Y?
# 
# First approach: simple scatter plot:
# 

# In[7]:

fig = plt.figure(figsize=(14,6))

n_points = 10000
x = np.exp(-np.random.randn(n_points))
# insert slight linear dependence! (0.1)
y = x*0.1 + np.random.randn(n_points)

ax1 = fig.add_subplot(121)
# alpha controls transparency
ax1.scatter(x,y, alpha=0.05, label="lin-lin scale")
ax1.legend()

ax2 = fig.add_subplot(122)
# alpha controls transparency
ax2.scatter(x,y, alpha=0.05, label="log-log scale")
ax2.legend()
ax2.set_xscale('log')


# Can we spot the slight trend?
# -----------------------------
#  
# **Compute bin-averages! (with binned_statistic):**
# 

# In[8]:

from scipy.stats import binned_statistic

# Note that the
# binned_statistic function above is not available at Aalto computers
# due to an outdated scipy version.
# To use binned_statistic (or binned_statistic_2d) functions 
# copy the file bs.py to your coding directory from the course web-page 
# and take it into use use it similarly with:
#
# from bs import binned_statistic

fig = plt.figure(figsize=(14,6))
# linear bins for the lin-scale:

n_bins = 20
bin_centers, _, _ = binned_statistic(x, x, statistic='mean', bins=n_bins)
bin_averages, _, _ = binned_statistic(x, y, statistic='mean', bins=n_bins)
ax1 = fig.add_subplot(121)

# Note: alpha controls the level of transparency
ax1.scatter(x,y, alpha=0.05, label="lin-lin")
ax1.plot(bin_centers, bin_averages, "ro-", label="avg")
ax1.legend(loc='best')
ax1.set_xlabel("x")
ax1.set_ylabel("y")
print "Note the missing points with larger values of x!"

# generate logarithmic x-bins
log_bins_for_x = np.logspace(np.log10(np.min(x)), np.log10(np.max(x)), num=n_bins)

# get bin centers and averages:
bin_centers, _, _ = binned_statistic(x, x, statistic='mean', bins=log_bins_for_x)
# Note: instead of just taking the center of each bin, it can be sometimes very important
# to set the x-value of abin to the actual mean of the x-values in that bin!
# (This is the case e.g. in the exercise discussing the Barabasi-Albert network!)

bin_averages, _, _ = binned_statistic(x, y, statistic='mean', bins=log_bins_for_x)

ax2 = fig.add_subplot(122)
ax2.scatter(x,y, alpha=0.06, label="log-log")
ax2.plot(bin_centers, bin_averages, "ro-", label="avg")
ax2.legend(loc='best')
ax2.set_xlabel("x")
ax2.set_ylabel("y")
ax2.set_xscale('log')


# Exercise: can you plot also the stdev of each bin using binned_statistic
# see the binned_statistic in scipy documentation and ax.errorbar()


# More sophisticated approaches for presenting 2D-distributions include e.g. heatmaps, which can be obtained using using binned_statistic2d and pcolor. 
# More of those later in the course!

# Summary:
# --------
# 
# * Know your data.
# * **Use proper axes that fit your purpose!**
# * **With log-log axes it is possible to 'zoom' into the tail.**
# * **Binning can be tricky**
#     * PDFs especially
#     * 1-CDFs helpful in investigating the tail + no need for binning
#    
plt.show()
