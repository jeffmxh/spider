# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import os
import time
import random


class Spider:
    def __init__(self):
        self.headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0'}

    def get_url_soup(self, url, encoding='gbk'):
        time.sleep(3 + 3 * random.random())
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


def parse_table(text):
    data = []
    table_body = text.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
    return data


def parse_single_list(soup):
    foo = soup.find_all('a')
    author_foo = [x for x in foo if re.search('author', str(x))][0]
    novel_foo = [x for x in foo if re.search('novel', str(x))][0]
    author_name = author_foo.get_text().strip()
    author_id = re.findall('authorid=([0-9]+)', str(author_foo))[0]
    novel_name = novel_foo.get_text().strip()
    novel_id = re.findall('novelid=([0-9]+)', str(novel_foo))[0]
    return '<author id="{}">{}</author><novel id="{}">{}</novel>'.format(author_id, author_name, novel_id, novel_name)

if __name__ == '__main__':
    time_stamp = time.strftime("%Y-%m-%d", time.localtime())
    spider = Spider()
    index_one = [3, 5, 4, 6, 9, 7, 8, 13, 15, 18, 19, 20, 21]
    for index in index_one:
        list_url = 'http://www.jjwxc.net/topten.php?orderstr={}&t=0'.format(index)
        list_soup = spider.get_url_soup(list_url)
        file_title = list_soup.find('span', class_='current').get_text().strip()
        file_title = file_title + '.txt'
        tables = list_soup.find_all('table')
        table_raw = [x for x in tables if re.search('作品积分', str(x))][0]
        result_table = parse_table(table_raw)
        result = ['\t'.join(x) for x in result_table]
        save_dir = os.path.join('save', 'toplist', time_stamp)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        file_name = os.path.join(save_dir, file_title)
        spider.write_list_txt(result, file_name)
        print('File : {} saved!'.format(file_name))


    index_two = [12, 16, 17]
    for index in index_two:
        list_url = 'http://www.jjwxc.net/topten.php?orderstr={}&t=0'.format(index)
        list_soup = spider.get_url_soup(list_url)
        file_title = list_soup.find('span', class_='current').get_text().strip()
        tables = list_soup.find_all('div', attrs={
                "class":["wrapper box_07", "wrapper box_07 ", "wrapper box_06", "wrapper box_06 "]})
        save_dir = os.path.join('save', 'toplist', time_stamp, file_title)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        for soup in tables:
            class_name = soup.h5.string
            class_name = re.sub('/', '_', class_name)
            class_name = class_name + '.txt'
            result = [parse_single_list(x) for x in tables[0].find_all('li')]
            file_name = os.path.join(save_dir, class_name)
            spider.write_list_txt(result, file_name)
            print('File : {} saved!'.format(file_name))