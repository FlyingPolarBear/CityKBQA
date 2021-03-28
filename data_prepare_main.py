'''
Author: Derry
Email: drlv@stu.xidian.edu.cn
Date: 2021-02-11 00:01:27
LastEditors: Derry
LastEditTime: 2021-02-22 23:35:01
Description: 数据准备的主函数
'''

from build_graph import *
from clean_data import *
from request_data import *

if __name__ == "__main__":
    collecter = InfoCollecter()
    collecter.pipeline()
    cleaner = DataCleaner()
    cleaner.pipeline()
    builder = GraphBuilder()
    builder.pipeline()
