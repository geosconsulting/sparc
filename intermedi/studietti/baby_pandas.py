__author__ = 'fabio.lana'
import numpy as np
import pandas as pd

df = pd.read_csv("train.csv")
# print df.head()
# print df.describe()
# print df.Age.median()
# print df['Sex'].unique()

import matplotlib.pyplot as plt
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.hist(df['Age'],bins=10,range = (df['Age'].min(),df['Age'].max()))
# plt.title('Age Distribution')
# plt.xlabel('Age')
# plt.ylabel('Count of Passengers')
#plt.show()

#df.boxplot(column='Fare')
#plt.show()

#df.boxplot(column='Fare', by = 'Pclass')
#plt.show()

temp1 = df.groupby('Pclass').Survived.count()
temp2 = df.groupby('Pclass').Survived.sum()/ df.groupby('Pclass').Survived.count()
fig1 = plt.figure(figsize=(8,4))

ax1 = fig1.add_subplot(121)
ax1.set_xlabel('Pclass')
ax1.set_ylabel('Count of Passengers')
ax1.set_title('Passengers by Pclass')
temp1.plot(kind='bar')

ax2 = fig1.add_subplot(122)
temp2.plot(kind='bar')
ax2.set_xlabel('Pclass')
ax2.set_ylabel('Probability of Survival')
ax2.set_title('Probability of Survival by Class')
#plt.show()

#temp3 = pd.crosstab([df.Pclass,df.Sex],df.Survived.astype(bool))
#temp3.plot(kind='bar',stacked = True, color=['red','blue'],grid=False)
#plt.show()

#temp4 = pd.crosstab([df.Pclass,df.Sex,df.Embarked], df.Survived.astype(bool))
#temp4.plot(kind='bar',stacked = True, color=['green','gray'],grid=True)
#plt.show()

#print sum(df['Cabin'].isnull())
df = df.drop(['Ticket','Cabin'], axis=1)

def name_extract(word):
    return word.split(',')[1].split('.')[0].strip()

df2 = pd.DataFrame({'Salutation': df['Name'].apply(name_extract)})
#print df2.head()

df = pd.merge(df, df2, left_index = True, right_index = True)
temp5 = df.groupby('Salutation').PassengerId.count()
#print temp5

def group_salutation(old_salutation):
 if old_salutation == 'Mr':
    return('Mr')
 else:
    if old_salutation == 'Mrs':
       return('Mrs')
    else:
       if old_salutation == 'Master':
          return('Master')
       else:
          if old_salutation == 'Miss':
             return('Miss')
          else:
             return('Others')

df3 = pd.DataFrame({'New_Salutation':df['Salutation'].apply(group_salutation)})
df = pd.merge(df, df3, left_index = True, right_index = True)
temp1 = df3.groupby('New_Salutation').count()
print df
df.boxplot(column='Age', by = 'New_Salutation')
df.boxplot(column='Age', by = ['Sex','Pclass'])
plt.show()

# df_sort = df.sort(['name'],ascending = True)
# #print df_sort.head()
#
# from datetime import datetime
# char_date = 'Apr 1 2015 1:20 PM'
# date_obj = datetime.strptime(char_date,'%b %d %Y %I:%M %p')
# print date_obj
