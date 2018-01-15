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


class Spider:
    def __init__(self):
        self.headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0'}

    def get_url_soup(self, url, encoding='gbk'):
        time.sleep(1 + 3 * random.random())
        response = requests.get(url, headers=self.headers)
        response.encoding = encoding
        soup = BeautifulSoup(response.text, 'lxml')
        return soup

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
    time.sleep(3 + 3 * random.random())
    browser = webdriver.PhantomJS()
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    browser.quit()
    return soup


def get_logger(filename):
    if not os.path.isdir('/home/da/spider/save/comments/log'):
        os.makedirs('/home/da/spider/save/comments/log')
    logger = logging.getLogger('my_logger' + filename)
    logger.setLevel(logging.DEBUG)
    # 建立一个filehandler来把日志记录在文件里，级别为debug以上
    fh = logging.FileHandler('/home/da/spider/save/comments/log/' + filename + ".log")
    fh.setLevel(logging.DEBUG)
    # 建立一个streamhandler来把日志打在CMD窗口上，级别为info以上
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # 设置日志格式
    formatter = logging.Formatter('[%(levelname)-3s]%(asctime)s %(filename)s[line:%(lineno)d]:%(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    #将相应的handler添加在logger对象中
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


def global_sleep(length):
    length = int(length)
    print('-----Start global sleep!-----')
    for i in range(length):
        time.sleep(1)
        print('Restart in %d seconds...' %(length-i))


def load_book_list(book_dir):
    books = pd.read_csv(book_dir, sep='\t',header=None)
    books.columns=['title','book_index']
    return books


def extract_single_reply(soup, spider):
    # 用户名
    try:
        info = spider.text_trim(re.findall('网友：(.+?)\u3000', str(soup))[0])
    except:
        info = "error"

    # 评分
    try:
        rating = re.findall('打分：([0-9]+)', str(soup))[0]
    except:
        rating = "error"

    # 评论正文
    try:
        pattern = re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(.+?)reply')
        content = re.sub('此评论发自晋江APP', '', spider.text_trim(pattern.findall(str(soup))[0]))
#         content = re.findall('</font><br>(.+?)<br><br>', str(soup))[0]
    except:
        content = "error"

    # 客户端
    try:
        device = soup.find("font", attrs={"color":"#009900", "size":"2"}).get_text()
    except:
        device = "error"

    # 时间
    try:
        time_pattern = re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
        time = time_pattern.findall(soup.script.get_text())[0]
    except:
        time = "error"

    return '<reply user_name="{}" device="{}" time="{}" rating="{}">{}</reply>'.format(
        info, device, time, rating, content)

def extract_all_reply(soup, spider):
    re_list = soup.find_all('div', attrs={"class":"replybody"})
    result = [extract_single_reply(x, spider) for x in re_list]
    return ''.join(result)

def extract_comment(soup, logger, spider):
    target = soup.find("div", attrs={"class":"readbody"})
    # 客户端
    try:
        device = target.find("font").get_text()
    except:
        device = "error"
    # 评论正文
    comment = re.sub(device, "", target.get_text().strip())
    comment = re.sub('\s+', '_', comment)
    # 用户名
    try:
        user_name = soup.find('span', attrs={"class":"blacktext"}).get_text()
    except:
        user_name = "error"
    # 用户id
    try:
        user_id = re.findall('readerid=([0-9]+)$', soup.find('a', attrs={"target":"_blank"})['href'])[0]
    except:
        user_id = "error"
    # 发表时间
    try:    
        foo = str(soup.find("span", attrs={"class":"coltext"}))
        time_pattern = re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
        time_stamp = time_pattern.findall(foo)[0]
    except:
        time_stamp = "error"
    # 评分
    try:
        rating = re.findall('<span class="blacktext">([0-9]+)</span>', str(soup))[0]
    except:
        rating = "error"
    # 所评章节
    try:
        chapter_id = re.findall('所评章节：([0-9]+)', str(soup))[0]
    except:
        chapter_id = "error"
    reply_content = extract_all_reply(soup, spider)
    main_result = '<comment user_name="{}" user_id="{}" device="{}" time="{}" rating="{}" chapter_id="{}">{}{}</comment>'.format(
        user_name, user_id, device, time_stamp, rating, chapter_id, comment, reply_content)
    # if user_id is not "error":
    #     parse_user(user_id, logger, spider)
    return main_result


def list_trim(tab):
    foo = [re.sub('\s+', '_', x) for x in tab]
    return '\t'.join(foo)

def parse_user(user_id, logger, spider):
    user_root_path = '/home/da/spider/save/users/'
    if not os.path.exists(user_root_path):
        os.mkdir(user_root_path)
    current_users = os.listdir(user_root_path)
    if user_id not in current_users:
        try:
            user_href = 'http://www.jjwxc.net/onereader.php?readerid={}'.format(user_id)
            user_soup = getPhantomSoup(user_href)
            # 订阅的作品
            recent_books = user_soup.find_all("div", attrs={"id":"load_show_vipServer"})[0]
            recent_list = spider.parse_table(recent_books)[1::2]
            recent_list = ['\t'.join(x) for x in recent_list]
            # 收藏的作品
            star_books = user_soup.find_all("div", attrs={"id":"load_show_novelsa"})[0]
            star_result = spider.parse_table(star_books)
            star_result = [list_trim(x) for x in star_result]
            # 用户名
            user_name = user_soup.find('span', attrs={"id":"favorite_reader"})['rel']
            # 存储数据
            user_path = user_root_path + user_id + '/'
            os.mkdir(user_path)
            spider.write_list_txt(recent_list, file_name=user_path+'订阅.txt')
            spider.write_list_txt(star_result, file_name=user_path+'收藏.txt')
            spider.write_txt(user_name, file_name=user_path+'用户名.txt')
            logger.info('User : {} parsed sucessfully!'.format(user_id))
        except:
            logger.info('User : {} parsed failed!'.format(user_id))
            # pass


def get_total_pages(novel_id, spider):
    comment_url = "http://www.jjwxc.net/comment.php?novelid={}&page=1".format(novel_id)
    comment_soup = spider.get_url_soup(comment_url)
    total_pages = int(comment_soup.h1.find_all('span')[1].string)
    return total_pages

def parse_comment(global_step, books, spider):
    novel_title = books.loc[global_step, 'title']
    novel_title = '%d.%s' % (global_step, novel_title)
    novel_id = books.loc[global_step, 'book_index']
    logger = get_logger('%s_%s' % (novel_title, novel_id))
    comment_path = '/home/da/spider/save/comments/' + novel_title + '/'
    if not os.path.exists(comment_path):
        os.makedirs(comment_path)
    if global_step < 100:
        total_pages = get_total_pages(novel_id, spider)
        done_pages = 10 * len(os.listdir(comment_path))
        stash_list = []
        count = 0
        if done_pages < total_pages:
            for page in range(done_pages, total_pages):
                try:
                    comment_url = "http://www.jjwxc.net/comment.php?novelid={}&page={}".format(novel_id, page)
                    comment_soup = spider.get_url_soup(comment_url)
                    comments = comment_soup.find_all("div", attrs={"id":re.compile("comment_[0-9]+")})
                    foo = [extract_comment(x, logger, spider) for x in comments]
                    stash_list.extend(foo)
                    count += 1
                    if count == 10:
                        file_name = comment_path + 'comment_page{}-{}.txt'.format(page-10, page)
                        spider.write_list_txt(stash_list, file_name)
                        logger.info('File : {} saved!'.format(file_name))
                        count = 0
                        stash_list.clear()
                    logger.info('Book : {} page : {}/{} parsed successfully! stash_list vol:{}'.format(novel_title, page, total_pages, len(stash_list)))
                except:
                    logger.info('Book : {} page : {}/{} parsed failed!'.format(novel_title, page, total_pages))
            logger.info('Book : {} comments parsed finished!'.format(novel_title))
    else:
        stash_list = []
        total_pages = get_total_pages(novel_id, spider)
        for page in range(total_pages):
            try:
                comment_url = "http://www.jjwxc.net/comment.php?novelid={}&page={}".format(novel_id, page)
                comment_soup = spider.get_url_soup(comment_url)
                comments = comment_soup.find_all("div", attrs={"id":re.compile("comment_[0-9]+")})
                foo = [extract_comment(x, logger, spider) for x in comments]
                stash_list.extend(foo) 
                logger.info('Book : {} page : {}/{} parsed successfully! stash_list vol:{}'.format(novel_title, page, total_pages, len(stash_list)))
            except:
                logger.info('Book : {} page : {}/{} parsed failed!'.format(novel_title, page, total_pages))
        file_name = comment_path + 'comment_{}.txt'.format(len(stash_list))
        spider.write_list_txt(stash_list, file_name)
        logger.info('File : {} saved!'.format(file_name))
        logger.info('Book : {} comments parsed finished!'.format(novel_title))


if __name__ == '__main__':
    books = load_book_list('/home/da/spider/book_list.txt')
    spider = Spider()
    current_step = len(os.listdir('/home/da/spider/save/comments/'))-2 +1
    total_step = len(books)
    parse_comment(2, books, spider)
    # for global_step in range(current_step, total_step):
    #     parse_comment(global_step, books, spider)
    #     global_sleep(30)
