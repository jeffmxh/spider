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
               "Cookie": ""}
    r = requests.get(url, headers=headers)
#     r.raise_for_status()
    r.encoding = encoding
    soup = BeautifulSoup(r.text, 'lxml')
    return soup

