# -*- coding: utf-8 -*-

import pandas as pd
import threading
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import os
import time
import random
import logging

'''
获取html原网页文本
参数：url，即要打开的网页链接
返回值：为html网页文本
'''

class Spider:
    def __init__(self):
        self.headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0'}

    def get_url_soup(self, url, encoding='gbk'):
        time.sleep(5 + 10 * random.random())
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
    #         r.encoding = 'utf-8'
        response.encoding = encoding
        soup = BeautifulSoup(response.text, 'lxml')
        return soup

    def get_html_text(self, url, encoding='gbk'):
        try:
            time.sleep(5 + 10 * random.random())
            r = requests.get(url, timeout = 30)
            r.raise_for_status()
            r.encoding = encoding
            return r.text
        except:
            return ""

    def parse_table(self, text):
        data = []
        table = text.find('table')
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])
        return data

    def text_trim(self, text):
        pattern = re.compile('，|<.+?>|\\u3000')
        text = pattern.sub(',', str(text))
        text = re.sub('，+|,+', ',', text)
        text = re.sub('^,|,$', '', text)
        return text

    def write_list_txt(self, data, file_name):
        assert isinstance(data, list)
        assert file_name.endswith('.txt')
        with open(file_name, 'w') as f:
            f.writelines('\n'.join(data))

    def write_txt(self, data, file_name):
        assert isinstance(data, str)
        assert file_name.endswith('.txt')
        with open(file_name, 'w') as f:
            f.write(data)

def getPhantomSoup(url):
    time.sleep(5 + 10 * random.random())
    browser = webdriver.PhantomJS()
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    return soup

def get_url_cookie(url, encoding='gbk'):
    time.sleep(5 + 5 * random.random())
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0",
               "Cookie": "ispayuser=3384244-1; foreverreader=3384244; CNZZDATA30075907=cnzz_eid%3D1647796701-1511356436-http%253A%252F%252Fwww.jjwxc.net%252F%26ntime%3D1512101636; timeOffset_o=221; __cfduid=d2f7d71ef3e8765791a18d648591ecf541512122483; UM_distinctid=16011860350c5-0d05b781c802798-70216751-1fa400-160118603515f4; testcookie=yes; Hm_lvt_bc3b748c21fe5cf393d26c12b2c38d99=1511759494,1511798904,1511842068,1511842070; Hm_lpvt_bc3b748c21fe5cf393d26c12b2c38d99=1512122503; need_auth_checked=yexuan2955@sina.com%3B-1%3B1512122495837%3Busername%3Dyexuan2955@sina.com%3Bisneed%3Dfalse%3Bip%3D202.119.42.228%3Bipcount%3D0%3Busernamecount%3D0; clicktype=; nicknameAndsign=2%257E%2529%2524%25E9%25A3%258E%25E8%25BF%2587; token=MzM4NDI0NHw1NWQ4MjNhMDkzNzZlM2FkZTYwZjdiYjRiMWQxOWJiYXx8eWV4KioqKioqKkBzaW5hLmNvbXwzNzk3NzN8fDF8MzM4NDI0NHx85qyi6L%2BO5oKo77yM5pmL5rGf55So5oi3fDF8ZW1haWw%3D; sms_total=0"}
    r = requests.get(url, headers=headers)
#     r.raise_for_status()
    r.encoding = encoding
    soup = BeautifulSoup(r.text, 'lxml')
    return soup

