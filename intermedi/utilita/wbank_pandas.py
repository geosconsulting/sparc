__author__ = 'fabio.lana'
from pandas.io import wb

#wb.search('gdp.*capita.*const').iloc[:,:2]

dat = wb.download(indicator='NY.GDP.PCAP.KD', country=['US', 'CA', 'MX'], start=2005, end=2013)
print dat

print dat['NY.GDP.PCAP.KD'].groupby(level=0).mean()

# ind = ['NY.GDP.PCAP.KD', 'IT.MOB.COV.ZS']
# dat_cell = wb.download(indicator=ind, country='all', start=2011, end=2011).dropna()
# dat_cell.columns = ['gdp', 'cellphone']
# print(dat_cell.tail())

# import numpy as np
# import statsmodels.formula.api as smf
# mod = smf.ols("cellphone ~ np.log(gdp)", dat_cell).fit()
# print(mod.summary())

#print wb.search('fertility rate')

import pycountry

nazione = pycountry.countries.get(alpha3='USA')
print nazione.alpha2