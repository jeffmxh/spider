# -*- coding: utf-8 -*-

import pandas as pd
import requests
import re
import os
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from spider import *
from logger import get_logger


def global_sleep(length):
    length = int(length)
    print('-----Start global sleep!-----')
    for i in range(length):
        time.sleep(1)
        print('Restart in %d seconds...' %(length-i))

def load_book_list(book_dir):
    books = pd.read_csv(book_dir, sep='\t',header=None)
    books.columns=['title','book_index']
    try:
        books_finish = os.listdir('/home/da/spider/save')
        books_finish = [re.sub('[0-9]+\.', '', x) for x in books_finish]
        result = books.loc[books['title'].map(lambda x:x not in books_finish),:]
    except:
        result = books
    return result

# 需求一：基本信息

def extract_info(text):
    filter_pattern = re.compile('<.+?>|\s')
    text = filter_pattern.sub(',', str(text))
    text = re.sub('^,+|,+$', '', text)
    text = re.sub(',+', ',', text)
    text = re.split(',', text)
    result = ''.join(text[1:])
    return result

# 需求四&五

def get_text_writer(chap_url, spider):
    if re.findall('vip', chap_url):
        chap_soup = get_url_cookie(chap_url)
        chap_text = str(chap_soup.find_all("div", attrs={"class":"noveltext"})[0])
        chap_text = chap_text.split('<div id="show"></div>')[1]
        chap_text = chap_text.split('<div')[0]
        result_text = spider.text_trim(chap_text)
    else:
        chap_soup = spider.get_url_soup(chap_url)
        chap_text = str(chap_soup.find_all("div", attrs={"class":"noveltext"})[0])
        chap_text = chap_text.split('<div style="clear:both;"></div>')[1]
        chap_text = chap_text.split('<div')[0]
        result_text = spider.text_trim(chap_text)
    try:
        writer_comment = chap_soup.find_all("div", attrs={"class":"readsmall"})[0]
        result_writer = spider.text_trim(writer_comment)
    except:
        result_writer = "None"
    return result_text, result_writer

def parse_book(global_step, books):
    novel_title = books.loc[global_step, 'title']
    novel_title = '%d.%s' % (global_step, novel_title)
    novel_id = books.loc[global_step, 'book_index']
    logger = get_logger('%s_%s' % (novel_title, novel_id))
    spider = Spider()

    logger.info('start getting book %d' %(global_step))
    url = 'http://www.jjwxc.net/onebook.php?novelid={}'.format(novel_id)
    soup = getPhantomSoup(url)
    logger.info('%s home_page downloaded!' % (novel_title))

    # 需求一：文案

    try:
        des = soup.find_all('div', attrs={'id':"novelintro", 'itemprop':"description"})[0]
        result_desp = spider.text_trim(des)
        if not os.path.exists('save/' + novel_title + '/task1'):
            os.makedirs('save/' + novel_title + '/task1')
        spider.write_txt(result_desp, 'save/' + novel_title + '/task1/description.txt')
        logger.info('%s task1:description parsed successfully!' % (novel_title))
    except:
        logger.info('%s task1:description parsed failed!' % (novel_title))

    # 需求一：标签

    try:
        result_tag = [x.get_text() for x in soup.find_all('font', attrs={"color":"#FF0000"})]
        spider.write_list_txt(result_tag, 'save/' + novel_title + '/task1/tags.txt')
        logger.info('%s task1:tags parsed successfully!' % (novel_title))
    except:
        logger.info('%s task1:tags parsed failed!' % (novel_title))

    # 需求一：关键字

    try:
        result_keywords = soup.find_all('span', attrs={"class":"bluetext"})[0].get_text()
        spider.write_txt(result_keywords, 'save/' + novel_title + '/task1/keywords.txt')
        logger.info('%s task1:keywords parsed successfully!' % (novel_title))
    except:
        logger.info('%s task1:keywords parsed failed!' % (novel_title))

    # 需求一：基本信息

    try:
        info = soup.find_all('ul', attrs={"class":"rightul", "name":"printright"})[0].find_all('li')
        result_info = [extract_info(x) for x in info]
        spider.write_list_txt(result_info, 'save/' + novel_title + '/task1/basic_info.txt')
        logger.info('%s task1:basic_info parsed successfully!' % (novel_title))
    except:
        logger.info('%s task1:basic_info parsed failed!' % (novel_title))

    # 需求一：地雷

    try:
        text = soup.find_all("div", attrs={"id":"ticketsrank_box"})[0]
        result_mine = ['\t'.join(x) for x in spider.parse_table(text)]
        spider.write_list_txt(result_mine, 'save/' + novel_title + '/task1/mine.txt')
        logger.info('%s task1:mine parsed successfully!' % (novel_title))
    except:
        logger.info('%s task1:mine parsed failed!' % (novel_title))

    # 需求二：章节信息

    try:
        if not os.path.exists('save/' + novel_title + '/task2'):
            os.makedirs('save/' + novel_title + '/task2')
        raw_table = soup.find_all("meta", attrs={"itemprop":"dateModified"})[0]
        chapter_table = spider.parse_table(raw_table)[3:]
        result_chap_table = ['\t'.join(x) for x in chapter_table]
        spider.write_list_txt(result_chap_table, 'save/' + novel_title + '/task2/chapter_table.txt')
        logger.info('%s task2:chapter_table parsed successfully!' % (novel_title))
    except:
        logger.info('%s task2:chapter_table parsed failed!' % (novel_title))

    # 需求二：成绩

    try:
        score = soup.find_all("td", attrs={"colspan":"6", "class":"sptd"})[1]
        text = score.get_text().strip()
        text = re.sub('\n|\u3000', '', text)
        result = re.split('\s+', text)
        spider.write_list_txt(result, 'save/' + novel_title + '/task2/score.txt')
        logger.info('%s task2:score parsed successfully!' % (novel_title))
    except:
        logger.info('%s task2:score parsed failed!' % (novel_title))

    # 需求四&五

    raw_table = soup.find_all("meta", attrs={"itemprop":"dateModified"})[0]
    chapter_info = raw_table.find_all("tr", attrs={"itemprop":["chapter", "chapter newestChapter"]})
    for i,x in enumerate(chapter_info):
        try:
            try:
                href = x.a['href']
            except :
                href = x.a['rel'][0]
        except:
            href = 'invalid_url'
        chapter_table[i].append(href)

    if not os.path.exists('save/' + novel_title + '/main'):
        os.makedirs('save/' + novel_title + '/main')
    if not os.path.exists('save/' + novel_title + '/writer_comment'):
        os.makedirs('save/' + novel_title + '/writer_comment')
    for i,chap in enumerate(chapter_table):
        try:
            chap_title = chap[1]
            chap_main, writer_main = get_text_writer(chap[-1], spider)
            spider.write_txt(chap_main.strip(),
                                  'save/' + novel_title +'/main/' + chap[0] + '.' + chap_title + '.txt')
            spider.write_txt(writer_main,
                               'save/' + novel_title + '/writer_comment/' + chap[0] + '.' + chap_title + '.txt')
            logger.info('{}:{}.{} task4:chapter parsed successfully!'.format(novel_title, chap[0], chap_title))
        except:
            logger.info('{}:{}.{} task4:chapter parsed failed!'.format(novel_title, chap[0], chap_title))

if __name__ == '__main__':
    books = load_book_list('/home/da/spider/book_list.txt')
    for global_step in books.index:
        parse_book(global_step, books)
        global_sleep(30)
