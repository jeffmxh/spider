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
        # time.sleep(3 + 3 * random.random())
        response = requests.get(url, headers=self.headers)
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


def list_trim(tab):
    foo = [re.sub('\s+', '_', x) for x in tab]
    return '\t'.join(foo)


def get_logger():
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)
    # 建立一个streamhandler来把日志打在CMD窗口上，级别为info以上
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # 设置日志格式
    formatter = logging.Formatter('[%(levelname)-3s]%(asctime)s %(filename)s[line:%(lineno)d]:%(message)s')
    ch.setFormatter(formatter)
    #将相应的handler添加在logger对象中
    logger.addHandler(ch)
    return logger


def load_users(file_name):
    user_root_path = 'save/users/'
    if not os.path.exists(user_root_path):
        os.mkdir(user_root_path)
    current_users = os.listdir(user_root_path)
    user_list = []
    with open(file_name, 'r') as f:
        for user in f.readlines():
            user_list.append(user.strip())
    TODO_users = list(set(user_list) - set(current_users))
    return TODO_users


def parse_recent_table(soup):
    data = []
    table_body = soup.find('table')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [re.sub('\n', '', ele.text.strip()) for ele in cols]
        data.append([ele for ele in cols if ele])
    return data


def parse_user(user_id, spider):
    user_root_path = 'save/users/'
    if not os.path.exists(user_root_path):
        os.mkdir(user_root_path)
    # 订阅的作品
    recent_url = 'http://www.jjwxc.net/onereader_ajax.php?readerid={}&action=show_vipServer'.format(user_id)
    recent_soup = spider.get_url_soup(recent_url, encoding='utf-8')
    time.sleep(0.5 + random.random())
    recent_list = parse_recent_table(recent_soup)
    recent_list = ['\t'.join(x) for x in recent_list][1::2]
    
    # 收藏的作品
    star_url = 'http://www.jjwxc.net/onereader_ajax.php?readerid={}&action=show_novelsa'.format(user_id)
    star_soup = spider.get_url_soup(star_url, encoding='utf-8')
    time.sleep(0.5 + random.random())
    star_result = parse_recent_table(star_soup)
    star_result = ['\t'.join(x) for x in star_result]
    
    # 用户名
    user_href = 'http://www.jjwxc.net/onereader.php?readerid={}'.format(user_id)
    user_soup = spider.get_url_soup(user_href)
    time.sleep(0.5 + random.random())
    user_name = user_soup.find('span', attrs={"id":"favorite_reader"})['rel']
    
    # 存储数据
    user_path = user_root_path + user_id + '/'
    os.mkdir(user_path)
    spider.write_list_txt(recent_list, file_name=user_path+'订阅.txt')
    spider.write_list_txt(star_result, file_name=user_path+'收藏.txt')
    spider.write_txt(user_name, file_name=user_path+'用户名.txt')
    time.sleep(1 + 3 * random.random())


def main():
    spider = Spider()
    logger = get_logger()
    TODO_users = load_users('users.txt')
    users_count = len(TODO_users)
    for i, user in enumerate(TODO_users):
        try:
            parse_user(user, spider)
            logger.info('Step {} of {}, User : {} parsed sucessfully!'.format(i+1, users_count, user))
        except:
            logger.info('Step {} of {}, User : {} parsed Failed!'.format(i+1, users_count, user))


if __name__ == '__main__':
    main()