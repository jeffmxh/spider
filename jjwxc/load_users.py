# coding: utf-8


import os
import re

import pandas as pd


def load_users(file_name):
    try:
        content = ''.join(pd.read_table(file_name, header=None)[0])
        pattern = re.compile('user_id="([0-9]+)"')
        users = set(pattern.findall(content))
    except:
        users = set()
    return users

def load_dir_users(dir_name):
    result = set()
    files = os.listdir(dir_name)
    files = [dir_name + x for x in files]
    for file in files:
        users = load_users(file)
        result = result | users
    return result

def load_all_users(dir_name):
    result = set()
    dirs = os.listdir(dir_name)
    for i, dir in enumerate(dirs):
        dir = dir_name + dir + '/'
        users = load_dir_users(dir)
        result = result | users
        print('%d of %d files finished! total users:%d' % (i+1, len(dirs), len(result)))
    return result


def write_list_txt(data, file_name):
    assert isinstance(data, list)
    assert file_name.endswith('.txt')
    with open(file_name, 'w') as f:
        f.writelines('\n'.join(data))


def main():
    all_users = load_all_users('save/comments/')
    write_list_txt(list(all_users), 'all_users.txt')
    print('All user list saved!')

    user_root_path = 'save/users/'
    if not os.path.exists(user_root_path):
        os.mkdir(user_root_path)
    current_users = os.listdir(user_root_path)
    TODO_users = list(set(all_users) - set(current_users))
    list1 = TODO_users[::2]
    list2 = TODO_users[1::2]
    write_list_txt(list1, 'todo_users1.txt')
    write_list_txt(list2, 'todo_users2.txt')
    print('Todo user lists saved!')

if __name__ == '__main__':
    main()
