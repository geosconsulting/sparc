__author__ = 'fabio.lana'
import statsmodels.api as sm
import pandas
from patsy import dmatrices


df = sm.datasets.get_rdataset("Guerry", "HistData").data
vars = ['Department', 'Lottery', 'Literacy', 'Wealth', 'Region']
df = df[vars]
df = df.dropna()

y, X = dmatrices('Lottery ~ Literacy + Wealth + Region', data=df, return_type='dataframe')

#print y[:3]
#print X[:3]
#print df[-5:]

mod = sm.OLS(y, X)
res = mod.fit()
#print res.summary()
#print res.params
print res.rsquared