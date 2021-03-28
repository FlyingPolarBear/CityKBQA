'''
Author: Derry
Email: drlv@stu.xidian.edu.cn
Date: 2021-02-07 22:34:14
LastEditors: Derry
LastEditTime: 2021-03-28 17:14:49
Description: 从百度百科中请求数据并解析，构建json格式的知识
'''

import time

import requests
from bs4 import BeautifulSoup
from utils import *
import threading


class InfoCollecter(object):
    def __init__(self):
        self.car2province = {'京': '北京市', '沪': '上海市', '津': '天津市', '渝': '重庆市', '蒙': '内蒙古自治区', '宁': '宁夏回族自治区', '新': '新疆维吾尔自治区', '苏': '江苏省',
                             '藏': '西藏自治区', '桂': '广西壮族自治区', '黑': '黑龙江省', '辽': '辽宁省', '吉': '吉林省', '冀': '河北省', '皖': '安徽省', '鄂': '湖北省', '湘': '湖南省',
                             '鲁': '山东省', '晋': '山西省', '陕': '陕西省', '甘': '甘肃省', '青': '青海省', '豫': '河南省', '浙': '浙江省', '赣': '江西省', '闽': '福建省', '粤': '广东省',
                             '琼': '海南省', '川': '四川省', '云': '云南省', '贵': '贵州省'}
        self.city_border = {}
        self.prov_border = {}
        self.city_info = {}
        self.prov_info = {}
        self.province = self.car2province.values()
        self.get_city_border()
        self.get_prov_border()

    def get_city_border(self):  # 加载城市集和接壤数据
        with open('data/origin/城市接壤数据.txt', encoding='utf-8') as f:
            for line in f:
                city1 = line.split('\t')[0]
                city2 = line.split('\t')[1].strip()
                if city1 not in self.city_border.keys():
                    self.city_border[city1] = []
                self.city_border[city1].append(city2)
        self.city_set = set(self.city_border.keys())
        self.city_num = len(self.city_set)

    def get_prov_border(self):  # 加载省份集和接壤数据
        with open('data/origin/省份接壤数据.txt', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                prov1 = line.split('\t')[0]
                prov2 = line.split('\t')[1:]
                self.prov_border[prov1] = prov2
        self.prov_set = set(self.prov_border.keys())
        self.prov_num = len(self.prov_set)

    def request_phrase_html(self, name):  # 从百度百科中请求数据并解析
        url = "https://baike.baidu.com/item/"+name
        headers = {"Cookie": "_uab_collina=160395250285657341202147; JSESSIONID=7C56E896658518A4E5BF99889839D00C; _jc_save_wfdc_flag=dc; _jc_save_fromStation=%u5317%u4EAC%2CBJP; _jc_save_toStation=%u4E0A%u6D77%2CSHH; BIGipServerotn=1725497610.50210.0000; RAIL_EXPIRATION=1604632917257; RAIL_DEVICEID=DeBrCMshZyD9JIK2yazJV4op0oxRXXKpeio_Y27U75ZkWKFwOd6Q_i2JRVBJeN3Q9qQ7ybyTw4Vv3ImAEwdTAAh8XLXL6WGn3irR65rZyYeWtvToLkq8oVAprmAw6OPgPnqI9a9ItALNr0kFjzDkncjjGPINbqfa; BIGipServerpassport=770179338.50215.0000; route=c5c62a339e7744272a54643b3be5bf64; _jc_save_fromDate=2020-11-02; _jc_save_toDate=2020-11-01",
                   "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"}
        requests.packages.urllib3.disable_warnings()
        r = requests.get(url, headers=headers, verify=False)
        r.encoding = r.apparent_encoding
        bs = BeautifulSoup(r.text, 'html.parser')
        summary = bs.find(
            'div', attrs={'class': "lemma-summary"}).text.split('\n')
        dt = bs.find_all('dt', attrs={'class': "basicInfo-item name"})
        dd = bs.find_all('dd', attrs={'class': "basicInfo-item value"})
        return summary, dt, dd

    def build_city_info(self, summary, dt, dd, city):  # 根据解析数据构建json格式的知识
        info = {}
        info['简介'] = ''.join(summary[i]
                             for i in range(1, len(summary), 2)).replace('"', '')
        for i in range(len(dt)):
            info[dt[i].text.strip().replace('\xa0', '')] = dd[i].text.strip().replace(
                ' ', '').split('\n')[0]
        city_info = {}
        city_info['属于'] = self.car2province[info['车牌代码'][0]]
        city_info['接壤'] = self.city_border[city]
        city_info['基本情况'] = info
        return city_info

    def build_prov_info(self, summary, dt, dd, prov):  # 根据解析数据构建json格式的知识
        info = {}
        info['简介'] = ''.join(summary[i]
                             for i in range(1, len(summary), 2)).replace('"', '')
        for i in range(len(dt)):
            info[dt[i].text.strip().replace('\xa0', '')] = dd[i].text.strip().replace(
                ' ', '').split('\n')[0]
        prov_info = {}
        prov_info['属于'] = '中华人民共和国'
        prov_info['接壤'] = self.prov_border[prov]
        prov_info['基本情况'] = info
        return prov_info

    def pipeline(self):
        count = 0
        # for prov in self.prov_set:
        #     count += 1
        #     start = time.time()
        #     try:
        #         summary, dt, dd = self.request_phrase_html(prov)
        #         self.prov_info[prov] = self.build_prov_info(
        #             summary, dt, dd, prov)
        #     except:
        #         print("！！出错省份：{}".format(prov))
        #         continue
        #     print("成功构建省份数据：{}\t进度：{}/{}\t时间：{:.2f}s".format(prov,
        #                                                      count, self.prov_num, time.time()-start))
        # dump_json(self.city_info, 'data/total/省份信息.json')
        # print("成功保存省份数据!")

        threads = []
        for city in self.city_set:
            thread = threading.Thread(target=self.build_city_info_thread,args=[city])
            threads.append(thread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        dump_json(self.city_info, 'data/total/城市信息.json')
        print("成功保存城市数据!")
    
    def build_city_info_thread(self, city):
        start = time.time()
        while True:
            try:
                summary, dt, dd = self.request_phrase_html(city)
                self.city_info[city] = self.build_city_info(
                    summary, dt, dd, city)
                break
            except:
                print("{} 请求失败，正在重试...".format(city))
                continue
        print("成功构建城市数据：{}\t时间：{:.2f}s".format(city, time.time()-start))


if __name__ == '__main__':
    collecter = InfoCollecter()
    collecter.pipeline()
