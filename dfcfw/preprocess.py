
# coding: utf-8

# In[1]:


import pandas as pd
import pickle
import re


# In[2]:


data1 = pd.read_excel('data/上市股票一览.xlsx')


# In[3]:


data2 = pd.read_excel('data/退市资料.xlsx')


# In[4]:


stock_dict = {}

stock1_code = list(data1.iloc[:, 0])
stock1_name = list(data1.iloc[:, 1])

for x,y in zip(stock1_code, stock1_name):
    code = re.sub('\.[A-Za-z]{2}$', '', str(x))
    stock_dict[code] = y
    
stock2_code = list(data2.iloc[:, 0])
stock2_name = list(data2.iloc[:, 1])

for x,y in zip(stock2_code, stock2_name):
    code = re.sub('\.[A-Za-z]{2}$', '', str(x))
    stock_dict[code] = y


# In[5]:


len(stock_dict)


# In[6]:


pickle.dump(stock_dict, open('static/stock_dict.pickle', 'wb'))


# In[7]:


pickle.dump(set(stock_dict.keys()), open('static/stock_code.pickle', 'wb'))

