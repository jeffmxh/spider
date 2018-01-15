# -*- coding: utf-8 -*-

import requests
import re
import os
import time
import logging
from spider import Spider

def get_books(rank_url):
    spider = Spider()
    base_soup = spider.get_url_soup(rank_url)
    table = base_soup.find_all('table', attrs={"class":"cytable"})[0]
    pattern_id = re.compile('novelid=([0-9]+)"')
    a = table.find_all('a', attrs={"class":"tooltip"})
    result = [(x.string, pattern_id.findall(str(x))[0]) for x in a]
    return result

def main():
    target_page = [1, 2, 150, 300, 450]
    base = "http://www.jjwxc.net/bookbase_slave.php?booktype=&opt=&page={}&endstr=true&orderstr=4"
    base_urls = [base.format(x) for x in target_page]
    book_list = []
    for url in base_urls:
        temp = get_books(url)
        time.sleep(3)
        book_list.extend(temp)
        print('%d books loaded!' % (len(book_list)))
    write_list = ['\t'.join(x) for x in book_list]
    spider = Spider()
    spider.write_list_txt(write_list, 'book_list.txt')

if __name__ == '__main__':
    main()