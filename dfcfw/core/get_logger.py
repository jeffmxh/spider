# coding: utf-8

"""
__title__ = 'get_logger.py'
__author__ = 'Jeffmxh'

                   _ooOoo_
                  o8888888o
                  88" . "88
                  (| -_- |)
                  O\  =  /O
               ____/`---'\____
             .'  \\|     |//  `.
            /  \\|||  :  |||//  \
           /  _||||| -:- |||||-  \
           |   | \\\  -  /// |   |
           | \_|  ''\---/''  |   |
           \  .-\__  `-`  ___/-. /
         ___`. .'  /--.--\  `. . __
      ."" '<  `.___\_<|>_/___.'  >'"".
     | | :  `- \`.;`\ _ /`;.`/ - ` : | |
     \  \ `-.   \_ __\ /__ _/   .-` /  /
======`-.____`-.___\_____/___.-`____.-'======
                   `=---='
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            佛祖保佑       永无BUG
"""

'''
设定日志文件格式
'''

import logging
import os

def get_logger(logger_name):
    if not os.path.isdir('log'):
        os.makedirs('log')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # 建立一个filehandler来把日志记录在文件里，级别为debug以上
    fh = logging.FileHandler('log/' + logger_name + ".log")
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

def get_stream_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # 建立一个streamhandler来把日志打在CMD窗口上，级别为info以上
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)-3s]%(asctime)s %(filename)s[line:%(lineno)d]:%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
