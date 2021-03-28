'''
Author: Derry
Email: drlv@stu.xidian.edu.cn
Date: 2021-02-10 12:38:01
LastEditors: Derry
LastEditTime: 2021-03-13 12:37:14
Description: 从清洗后的json知识中创建图数据
'''

import json
import time
from py2neo import Graph, Node, Relationship


class GraphBuilder(object):
    def __init__(self):
        self.graph = Graph(host="localhost", http_port=7474,
                           user="neo4j", password="456123")
        with open('data/total/城市信息_清洗后.json', encoding='utf-8') as f:
            self.city_info = json.load(f)
        with open('data/total/省份信息_清洗后.json', encoding='utf-8') as f:
            self.prov_info = json.load(f)
        self.border_head_cities = set()
        self.border_head_provs = set()

    def create_node(self, label, name, property):  # 生成节点
        query = "CREATE (n:"+label+" {name:'"+name+"',"
        for key, value in property.items():
            query += key+':"'+value+'",'
        query = query[:-1]+"}) RETURN n"
        self.graph.run(query)
        print("成功创建结点：{}".format(name))

    def create_belong_relation(self, city, province):  # 创建属于关系
        query = f"MATCH (n) WHERE n.name='{city}' RETURN n"
        citynode = self.graph.run(query).data()[0]['n']
        query = f"MATCH (n) WHERE n.name='{province}' RETURN n"
        provincenode = self.graph.run(query).data()[0]['n']
        self.graph.create(Relationship(citynode, "属于", provincenode))
        print(city, "属于", province)

    def create_city_border_relation(self, city, border_cities):  # 创建接壤关系
        query = f"MATCH (n:`城市`) WHERE n.name='{city}' RETURN n"
        match1 = self.graph.run(query).data()[0]['n']
        for border_city in border_cities:
            if border_city not in self.border_head_cities and border_city in self.city_info.keys():
                query = f"MATCH (n:`城市`) WHERE n.name='{border_city}' RETURN n"
                match2 = self.graph.run(query).data()[0]['n']
                self.graph.create(Relationship(match1, "接壤", match2))
                print("成功创建关系", city, "接壤", border_city)
        self.border_head_cities.add(city)

    def create_prov_border_relation(self, prov, border_provs):  # 创建接壤关系
        query = f"MATCH (n:`省份`) WHERE n.name='{prov}' RETURN n"
        match1 = self.graph.run(query).data()[0]['n']
        for border_prov in border_provs:
            if border_prov not in self.border_head_provs and border_prov in self.prov_info.keys():
                query = f"MATCH (n:`省份`) WHERE n.name='{border_prov}' RETURN n"
                match2 = self.graph.run(query).data()[0]['n']
                self.graph.create(Relationship(match1, "接壤", match2))
                print("成功创建关系", prov, "接壤", border_prov)
        self.border_head_provs.add(prov)

    def delete_whole_graph(self):  # 删除所有节点和关系
        start = time.time()
        self.graph.run('MATCH (n) DETACH DELETE n')
        print("成功删除所有节点和关系！(time={:.2f}s)".format(time.time()-start))

    def pipeline(self):
        start = time.time()
        self.graph.create(Node("国家", name="中华人民共和国"))
        for prov_name, prov_property in self.prov_info.items():
            self.create_node('省份', prov_name, prov_property['基本情况'])
            self.create_belong_relation(prov_name, prov_property['属于'])
        for prov_name, prov_property in self.prov_info.items():
            self.create_prov_border_relation(prov_name, prov_property['接壤'])
        for city_name, city_property in self.city_info.items():
            self.create_node('城市', city_name, city_property['基本情况'])
            self.create_belong_relation(city_name, city_property['属于'])
        for city_name, city_property in self.city_info.items():
            self.create_city_border_relation(city_name, city_property['接壤'])
        print("图数据库构建完成！(time={:.2f}s)".format(time.time()-start))


if __name__ == '__main__':
    builder = GraphBuilder()
    builder.pipeline()
    # builder.delete_whole_graph()
