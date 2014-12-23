# coding: utf-8

# In[3]:

# Import all libraries needed for the tutorial

# General syntax to import specific functions in a library: 
##from (library) import (specific library function)
from pandas import DataFrame, read_csv

# General syntax to import a library but no functions: 
##import (library) as (give the library a nickname/alias)
import matplotlib.pyplot as plt
import pandas as pd #this is how I usually import pandas
import sys #only needed to determine Python version number

# Enable inline plotting
#get_ipython().magic(u'matplotlib inline')


# In[4]:

file_popolazione = "Population_E_All_Data.csv"
df_popolazione = pd.read_csv(file_popolazione,index_col=0,header=0)


# In[5]:

solo_necessari = df_popolazione[['Country','Element','Year','Value']]
#print solo_necessari.head(10)
per_paese = solo_necessari[solo_necessari['Country'] == 'Cameroon'][:55]


# In[6]:

per_paese['Element'].describe()


# In[7]:

per_paese['Element'].unique()


# In[8]:
element = per_paese.groupby('Element')

# In[24]:
per_paese.head(5)

# In[10]:
per_paese_per_anno = per_paese.set_index('Year')

# In[11]:
per_paese_per_anno.plot()


# In[12]:

per_paese_per_anno.max()


# In[13]:

per_paese_per_anno.head(10)


# In[14]:

maskera = per_paese['Element'] == 'Total Population - Both sexes'
adesso = per_paese[maskera]


# In[15]:

adesso.head(5)


# In[16]:

pop_61 = adesso[['Year','Value']][adesso['Year']<=1965]


# In[17]:

cambio = pop_61.set_index('Year')


# In[18]:

cambio


# In[19]:

cambio.plot()


# In[20]:

cambio.to_excel("cambio.xls")


# In[25]:

cambio.to_csv("cambio.txt")


# In[29]:

per_paese_per_anno.to_json("paese_anno.json")

