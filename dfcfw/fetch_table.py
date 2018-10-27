
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
from collections import namedtuple
from core.get_logger import get_logger


# In[2]:


import json
import os
import random
import re
import requests
import time
import pickle


# In[3]:


time_stamp = time.strftime('%Y%m%d',time.localtime(time.time()))


# In[4]:


logger = get_logger('spider_'+time_stamp)


# In[5]:


def my_sleep():
    time.sleep(1 + 0.5 * random.random())


# In[6]:


class stock_pack:
    def __init__(self, data):
        self.data = data
        self.code = data['CDSY_SECUCODES'][0]['SECURITYCODE']
        self.url = data['Url']
        self.title = data['NOTICETITLE']
        
    def __str__(self):
        return 'stock_code: {} \ntitle: {}\nnotice_url: {}'.format(self.code, self.title, self.url)


# In[7]:


def is_annual(dp):
    return dp['ANN_RELCOLUMNS'][0]['COLUMNNAME'] == '年度报告全文' and not re.search('英文版|摘要', dp['NOTICETITLE'])


# In[13]:


def parse_detail_url(stock_code, step=0, logger):
    notice = []
    url_template = 'http://data.eastmoney.com/notices/getdata.ashx?StockCode={}&CodeType=1&PageIndex={}&PageSize=50&SecNodeType=0&FirstNodeType=0&rt=51339041'
    warning_times = 0
    page_index = 1
    while True:
        logger.info('Global step: {}/3666 Crawling stock: {} page: {} current_size: {} warnings: {}'.format(step, stock_code, page_index, len(notice), warning_times))
        my_sleep()
        try:
            url = url_template.format(stock_code, page_index)
#             print(url)
            html = requests.get(url)
            text = re.sub('^var  = |;$', '', html.text)
            data_pack = json.loads(text)
            assert data_pack['data']
            new_notice = [stock_pack(x) for x in data_pack['data'] if is_annual(x)]
            notice.extend(new_notice)
            warning_times = 0
        except:
            warning_times += 1
        finally:
            page_index += 1
        if warning_times >= 5:
            break
    return notice


# In[11]:


stock_code = pickle.load(open('static/stock_code.pickle', 'rb'))


# In[20]:


try:
    stock_data = pickle.load(open('output/stock_299.pickle', 'rb'))
except:
    stock_data = {}
current_step = len(stock_data)

for i,code in enumerate(stock_code):
    if i < current_step:
        continue
    else:
        foo = parse_detail_url(code, i, logger)
        stock_data[code] = foo
        if (i+1) % 300 == 0:
            pickle.dump(stock_data, open('output/stock_{}.pickle'.format(i), 'wb'))


# In[21]:


pickle.dump(stock_data, open('output/stock_{}.pickle'.format(i), 'wb'))


# In[22]:


i


# In[18]:


stock_data = pickle.load(open('output/stock_3666.pickle', 'rb'))


# In[19]:


len(stock_data)

