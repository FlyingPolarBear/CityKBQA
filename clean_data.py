'''
Author: Derry
Email: drlv@stu.xidian.edu.cn
Date: 2021-02-10 21:18:48
LastEditors: Derry
LastEditTime: 2021-04-16 21:28:28
Description: 清洗数据，保留出现次数较高的属性
'''

import time
from utils import *


class DataCleaner(object):
    def __init__(self):
        self.city_info = load_json('data/total/城市信息.json')
        self.prov_info = load_json('data/total/省份信息.json')
        with open('data/origin/民族.txt', encoding='utf-8') as f:
            self.nations = set()
            for line in f:
                self.nations.add(line.strip())
        self.city_property_dict = {}
        self.prov_property_dict = {}
        self.selected_city_info = {}
        self.selected_prov_info = {}

    def select_property(self, city_info):  # 统计城市中的主要属性
        prop2count = {}
        property_dict = {}
        for property in city_info.values():
            for prop in property['基本情况']:
                if prop not in prop2count.keys():
                    prop2count[prop] = 0
                prop2count[prop] += 1
        for prop, count in prop2count.items():
            if count >= 0.3 * len(city_info):
                property_dict[prop] = ''
        return property_dict

    def property_filter(self, city_info):  # 城市主要属性过滤
        selected_city_info = {}
        for name, property in city_info.items():
            selected_property = {}
            selected_property['属于'] = property['属于']
            selected_property['接壤'] = property['接壤']
            selected_property['基本情况'] = {}
            for prop in property['基本情况']:
                if prop in self.city_property_dict.keys():
                    selected_property['基本情况'][prop] = property['基本情况'][prop]
            for prop in self.city_property_dict.keys():
                if prop not in property['基本情况'].keys():
                    selected_property['基本情况'][prop] = '资料暂缺'
            selected_city_info[name] = selected_property
        return selected_city_info

    def get_another_names(self, selected_info):
        another_names = []
        end_words = ['市', '地区', '盟', '自治州', '省', '自治区', '特别行政区']
        for city_name in selected_info.keys():
            another_name = [city_name]  # eg.新疆维吾尔自治区
            for end_word in end_words:
                if city_name.endswith(end_word):
                    another_name.append(city_name[:-len(end_word)])  # eg.新疆维吾尔
            if city_name.endswith('自治州') or city_name.endswith('自治区'):
                another_name.append(city_name[:-3]+city_name[-1])  # eg.新疆维吾尔区
                location = len(city_name)-1
                for n in self.nations:
                    loc = city_name.find(n)
                    if loc != -1 and loc < location:
                        location = loc
                    if len(n) >= 2:
                        loc = city_name.find(n[:-1])
                        if loc != -1 and loc > 1 and loc < location:
                            location = loc
                if location >= 0 and location < len(city_name):
                    another_name.append(city_name[:location])  # eg.新疆
                    another_name.append(
                        city_name[:location]+city_name[-1])  # eg.新疆区
            another_names.append(another_name)
        return another_names

    def save_selected_info(self):  # 保存过滤主要属性的城市和省份数据
        dump_json(self.selected_city_info, 'data/total/城市信息_清洗后.json')
        dump_json(self.selected_prov_info, 'data/total/省份信息_清洗后.json')
        WriteText('data/final/城市属性.txt',
                  '\n'.join([prop for prop in self.city_property_dict.keys()]))
        WriteText('data/final/省份属性.txt',
                  '\n'.join([prop for prop in self.prov_property_dict.keys()]))
        WriteText('data/final/城市列表.txt',
                  '\n'.join([city_name for city_name in self.selected_city_info.keys()]))
        WriteText('data/final/城市列表及别称.txt',
                  '\n'.join([' '.join(city_name) for city_name in self.city_names]))
        WriteText('data/final/省份列表.txt',
                  '\n'.join([prov_name for prov_name in self.selected_prov_info.keys()]))
        WriteText('data/final/省份列表及别称.txt',
                  '\n'.join([' '.join(prov_name) for prov_name in self.prov_names]))

    def pipeline(self):
        start = time.time()
        self.city_property_dict = self.select_property(self.city_info)
        self.selected_city_info = self.property_filter(self.city_info)
        self.city_names = self.get_another_names(self.selected_city_info)
        self.prov_property_dict = self.select_property(self.prov_info)
        self.selected_prov_info = self.property_filter(self.prov_info)
        self.prov_names = self.get_another_names(self.selected_prov_info)
        self.save_selected_info()
        print("成功保存筛选属性后的数据!(time={:.2f}s)".format(time.time()-start))


if __name__ == '__main__':
    dc = DataCleaner()
    dc.pipeline()
