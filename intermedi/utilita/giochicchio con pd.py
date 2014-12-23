__author__ = 'fabio.lana'

from pandas import DataFrame,read_csv
import pandas as pd
import matplotlib.pyplot as plt
import sys

#d = [0,1,2,3,4,5,6,7,8,9]

d = {'one':[1, 1, 1, 1, 1],
     'two':[2, 2, 2, 2, 2],
     'letter':['a', 'a', 'b', 'b', 'c']}

df = pd.DataFrame(d)
# print df
# print df.iloc[2:6]

# Create group object
one = df.groupby('letter')

# Apply sum function
#print one.sum()

letterone = df.groupby(['letter', 'one']).sum()
#print letterone
#print letterone.index

lettertwo = df.groupby(['letter', 'two']).sum()
#print lettertwo

# Create a dataframe with dates as your index
States = ['NY', 'NY', 'NY', 'NY', 'FL', 'FL', 'GA', 'GA', 'FL', 'FL']
data = [1.0, 2, 3, 4, 5, 6, 7, 8, 9, 10]
idx = pd.date_range('1/1/2012', periods=10, freq='MS')
df1 = pd.DataFrame(data, index=idx, columns=['Revenue'])
df1['State'] = States

# Create a second dataframe
data2 = [10.0, 10.0, 9, 9, 8, 8, 7, 7, 6, 6]
idx2 = pd.date_range('1/1/2013', periods=10, freq='MS')
df2 = pd.DataFrame(data2, index=idx2, columns=['Revenue'])
df2['State'] = States

