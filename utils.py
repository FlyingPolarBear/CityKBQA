'''
Author: Derry
Email: drlv@stu.xidian.edu.cn
Date: 2021-01-22 22:16:14
LastEditors: Derry
LastEditTime: 2021-03-14 00:33:16
Description: 工具箱
'''
import json


def load_json(filepath):
    with open(filepath, encoding='utf-8') as f:
        content = json.load(f)
    return content


def dump_json(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=4, ensure_ascii=False)


def load_list(filepath):
    content = []
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            content.append(line.strip())
    return content


def WriteText(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)


def AddText(filename, content):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(content)


def LoadText(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    return text
