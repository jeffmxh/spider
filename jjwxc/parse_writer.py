
# coding: utf-8

# In[1]:



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
        time.sleep(5 + 5 * random.random())
        response = requests.get(url, headers=self.headers)
#         response.raise_for_status()
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
        pattern = re.compile('，|<.+?>|\\u3000|\s')
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
    time.sleep(5 + 5 * random.random())
    browser = webdriver.PhantomJS()
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    return soup


# In[2]:

def global_sleep(length):
    length = int(length)
    print('-----Start global sleep!-----')
    for i in range(length):
        time.sleep(1)
        print('Restart in %d seconds...' %(length-i))


# In[3]:

def load_book_list(book_dir):
    books = pd.read_csv(book_dir, sep='\t',header=None)
    books.columns=['title','book_index']
    return books


# In[4]:

def parse_table(text):
    data = []
    table_body = text.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
    return data


# In[5]:

def friend_link(soup):
    try:
        author_name = soup.text.strip()
    except:
        author_name = "error"
    try:
        author_id = re.findall('authorid=([0-9]+)', str(soup))[0]
    except:
        author_id = "error"
    return '<name>{}</name><id>{}</id>'.format(author_name, author_id)

def extract_link(soup):
    tables = soup.find_all('table')
    foo = [x for x in tables if re.search('友情链接', str(x))][0]
    links = foo.find_all('a')
    result_list = [friend_link(link) for link in links]
    return result_list


# In[6]:

# 霸王排行榜
def parse_bawang(author_soup):
    author_soup.find_all('div', attrs={"class":"next_content"})
    table_body = author_soup.find_all('div', attrs={"class":"bawangpiao_c"})[0]

    data = []
    rows = table_body.find_all('dl')
    for row in rows:
        user_id = re.findall('readerid=([0-9]+)', str(row))[0]
        cols = row.find_all('dt')
        cols = [ele.text.strip() for ele in cols]
        ftag = row.find('dd').text.strip()
        cols.append(ftag)
        cols.append(user_id)
        data.append([ele for ele in cols if ele])

    bawang_list = ['\t'.join(x) for x in data]
    return bawang_list


# In[7]:

# 作品列表

def parse_book_list(author_soup):
    try:
        tables = author_soup.find_all('table')
        foo = [x for x in tables if re.search('风格', str(x))][0]
        book_list = parse_table(foo)
        result = ['\t'.join(x) for x in book_list]
    except:
        result = []
    return result


# In[17]:

def parse_writer(author_id, spider):
    author_url = 'http://www.jjwxc.net/oneauthor.php?authorid={}'.format(author_id)
    author_soup = getPhantomSoup(author_url)
    author_name = author_soup.title.get_text().strip()
    print('Parsing author:{} id:{}'.format(author_name, author_id))
    # 主页主题
    try:
        main_theme = author_soup.find_all('span', attrs={"class":"volumnfont"})[0].get_text().strip()
    except:
        main_theme = "error"
        print('main theme Failed!')
        
    # 主体文字
    try:
        main_text = spider.text_trim(author_soup.find_all('span', attrs={"itemprop":"description"})[0].get_text())
    except:
        main_text = "error"
        print('main text Failed!')
    
    # 主人告示
    try:
        div_list = author_soup.find_all('div')
        notice = [x for x in div_list if re.search('主人告示', str(x))][0]
        notice = re.sub('告示,', '告示:', spider.text_trim(notice))
    except:
        notice = "error"
        print('notice Failed!')
    
    # 微博链接
    try:
        weibo_url = author_soup.find_all('span', attrs={"itemprop":"description"})[0].a['href']
    except:
        weibo_url = "error"
        
    # 被收藏数
    try:
        favorite_count = re.findall('(被收藏数：[0-9]+)', str(author_soup))[0]
    except:
        favorite_count = "error"
        print('favorite count Failed!')
        
    # 作者送出的红包
    try:
        pkg = re.findall('(作者已送出[0-9]+个红包啦)', str(author_soup))[0]
    except:
        pkg = "error"
#         print('pkgs count Failed!')
    
    # 霸王榜单
    try:
        bawang_list = parse_bawang(author_soup)
    except:
        bawang_list = []
        print('bawang Failed!')
        
    # 最近更新作品信息
    try:
        recent_soup = author_soup.find_all('td', attrs={"height":"38", "align":"center", "bgcolor":"#eefaee"})[0]
        title = recent_soup.a.string.strip()
    except:
        title = ""
        print('title info Failed!')
    try:
        status = re.findall('连载中|已完成|暂停', str(recent_soup))[0]
    except:
        status = ""
        print('status Failed!')
    try:
        word_count = re.findall('>([0-9]+)<', str(recent_soup))[0]
    except:
        word_count = ""
        print('word count Failed!')
    try:
        time_stamp = re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(recent_soup))[0]
    except:
        time_stamp = ""
        print('time_stamp Failed!')
    recent_info = '<recent_info title="{}" status="{}" word_count="{}" time="{}">'.format(title, status, word_count, time_stamp)
    book_list = parse_book_list(author_soup)
    friend_links = extract_link(author_soup)
    result_1 = []
    result_1.append('<作者>{}</作者>'.format(author_name))
    result_1.append('<主页主题>{}</主页主题>'.format(main_theme))
    result_1.append('<正文>{}</正文>'.format(main_text))
    result_1.append('<告示>{}</告示>'.format(notice))
    result_1.append('<被收藏数>{}</被收藏数>'.format(favorite_count))
    result_1.append('<weibo>{}</weibo>'.format(weibo_url))
    result_1.append('<红包>{}</红包>'.format(pkg))
    result_1.append(recent_info)
    filedir = '/home/da/spider/save/author/'
    save_dir = filedir + author_id + '/'
    if not os.path.exists(save_dir):
        os.makedirs(filedir + author_id)
    spider.write_list_txt(result_1, save_dir+'basic_info.txt')
    spider.write_list_txt(bawang_list, save_dir+'霸王榜单.txt')
    spider.write_list_txt(book_list, save_dir+'作品列表.txt')
    spider.write_list_txt(friend_links, save_dir+'友情链接.txt')


# In[ ]:

spider = Spider()
books = load_book_list('/home/da/spider/book_list.txt')
for book_index in books.book_index:
    book_url = 'http://www.jjwxc.net/onebook.php?novelid={}'.format(book_index)
    book_soup = spider.get_url_soup(book_url)
    author_url = book_soup.h2.a['href']
    author_id = re.findall('authorid=([0-9]+)', author_url)[0]
    done_list = os.listdir('/home/da/spider/save/author/')
    if author_id not in done_list:
        parse_writer(author_id, spider)

