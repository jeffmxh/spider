
# coding: utf-8

# In[1]:


import json
import os
import random
import re
import requests
import time
import pickle


# In[2]:


from bs4 import BeautifulSoup
from collections import namedtuple, defaultdict
from core.get_logger import get_logger


# In[3]:


context_node = namedtuple('context_node', 'code title context')


# In[4]:


time_stamp = time.strftime('%Y%m%d',time.localtime(time.time()))


# In[5]:


logger = get_logger('spider_detail'+time_stamp)


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


def my_sleep():
    time.sleep(1 + 0.5 * random.random())


# In[8]:


def parse_title(soup):
    title = soup.find('div', attrs={'class': 'detail-header'}).get_text()
    title = re.sub('(\s|查看PDF原文)+', '----', title)
    title = re.sub('^----|----$', '', title)
    return title


# In[9]:


def parse_context(soup):
    context = soup.find('div', attrs={'class': 'detail-body'}).get_text()
    context = re.sub('^\s+|\s+$', '', context)
    return context


# In[10]:


def parse_detail(code, url):
    my_sleep()
    headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    title = parse_title(soup)
    context = parse_context(soup)
    result = context_node(code, title, context)
    return result


# In[21]:


def get_ckpt():
    files = os.listdir('output/')
    files = [x for x in files if re.search('stock_data_all_\d+.pickle', x)]
    files = [(x, int(re.findall('stock_data_all_(\d+).pickle', x)[0])) for x in files]
    files = sorted(files, key=lambda x: -x[1])
    file = files[0]
    return file[0], file[1]


# In[12]:


stock_data = pickle.load(open('output/stock_3666.pickle', 'rb'))


# In[ ]:


try:
    current_ckpt, current_step = get_ckpt()
    stock_data_all = defaultdict(list) #pickle.load(open(current_ckpt, 'rb'))
except:
    stock_data_all = defaultdict(list)
    current_step = 0

for global_step,(stock_code,stock_detail) in enumerate(stock_data.items()):
    if global_step <= current_step:
        continue
    else:
        for local_step,stock_node in enumerate(stock_detail):
            try:
                code = stock_node.code
                title = stock_node.title
                url = stock_node.url
                detail_data = parse_detail(code, url)
                temp = {'code': code, 'title': title, 'url': url, 'detail': detail_data}
                stock_data_all[code].append(temp)
                logger.info('Global step: {}/{} Local step: {}/{} stock_code: {} title: {}'.format(
                    global_step+1, len(stock_data), local_step+1, len(stock_detail), code, title))
            except:
                logger.error('Warning: Global step: {}/{} Local step: {}/{} stock_code: {} Failed!!'.format(
                    global_step+1, len(stock_data), local_step+1, len(stock_detail), code))
        if (global_step+1) % 500 == 0:
            pickle.dump(dict(stock_data_all), open('output/stock_data_all_{}.pickle'.format(global_step), 'wb'))
            stock_data_all = defaultdict(list)

