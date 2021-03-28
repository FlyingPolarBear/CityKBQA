'''
Author: Derry
Email: drlv@stu.xidian.edu.cn
Date: 2021-02-10 12:38:01
LastEditors: Derry
LastEditTime: 2021-03-28 22:46:33
Description: 从清洗后的json知识中创建图数据
'''

import time

from py2neo import Graph, Node, Relationship

from utils import *


class GraphBuilder(object):
    def __init__(self):
        self.graph = Graph(host="localhost", http_port=7474,
                           user="neo4j", password="456123")
        self.city_info = load_json('data/total/城市信息_清洗后.json')
        self.prov_info = load_json('data/total/省份信息_清洗后.json')
        self.sai_info = self.load_sai_info('data/added_knowledge/sai_data.txt')
        self.border_head = set()
        self.border_head_provs = set()

    def load_sai_info(self, data_path):
        sai_info = {}
        with open(data_path, encoding='utf-8') as f:
            for line in f:
                sai_info[line.split()[1]] = line.split()[2]
        return sai_info

    def create_node(self, label, name, property):  # 生成节点
        query = "CREATE (n:"+label+" {name:"+'"'+name+'",' + \
            'introduction:"'+property['简介']+'"}) RETURN n'
        self.graph.run(query)
        print("成功创建结点：{}".format(name))

    def create_belong_relation(self, city, province):  # 创建属于关系
        query = f"MATCH (n) WHERE n.name='{city}' RETURN n"
        citynode = self.graph.run(query).data()[0]['n']
        query = f"MATCH (n) WHERE n.name='{province}' RETURN n"
        provincenode = self.graph.run(query).data()[0]['n']
        self.graph.create(Relationship(citynode, "属于", provincenode))
        print(city, "属于", province)

    def create_border_relation(self, head_entity, border_entities):  # 创建接壤关系
        query = f"MATCH (n) WHERE n.name='{head_entity}' RETURN n"
        match1 = self.graph.run(query).data()[0]['n']
        for border_entity in border_entities:
            if border_entity not in self.border_head:
                query = f"MATCH (n) WHERE n.name='{border_entity}' RETURN n"
                match2 = self.graph.run(query).data()
                if len(match2) == 0:
                    self.graph.create(Node('其他', name=border_entity))
                    match2 = self.graph.run(query).data()
                match2 = match2[0]['n']
                self.graph.create(Relationship(match1, "接壤", match2))
                print("成功创建关系", head_entity, "接壤", border_entity)
        self.border_head.add(head_entity)

    def create_other_relation(self, entity, property, content):
        query = f'MATCH (n) WHERE n.name="{entity}" RETURN n'
        match1 = self.graph.run(query).data()[0]['n']
        query = f'MATCH (n) WHERE n.name="{content}" RETURN n'
        match2 = self.graph.run(query).data()
        if len(match2) == 0:
            self.graph.create(Node(property, name=content))
            match2 = self.graph.run(query).data()
        match2 = match2[0]['n']
        self.graph.create(Relationship(match1, property, match2))
        print("成功创建关系", entity, property, content)
    
    def create_sai_relation(self, property, entity):
        query = 'MATCH (n) WHERE n.name="人工智能学院" RETURN n'
        match1 = self.graph.run(query).data()[0]['n']
        query = f'MATCH (n) WHERE n.name="{entity}" RETURN n'
        match2 = self.graph.run(query).data()[0]['n']
        self.graph.create(Relationship(match1, property, match2))
        print("成功创建关系", "人工智能学院", property, entity)

    def delete_whole_graph(self):  # 删除所有节点和关系
        start = time.time()
        self.graph.run('MATCH (n) DETACH DELETE n')
        # self.graph.run("MATCH (n) WHERE n.name='西电' DELETE n")
        print("成功删除所有节点和关系！(time={:.2f}s)".format(time.time()-start))

    def pipeline(self):
        start = time.time()
        # self.graph.create(Node("国家", name="中华人民共和国"))
        # for prov_name, prov_property in self.prov_info.items():
        #     self.create_node('省份', prov_name, prov_property['基本情况'])
        # for city_name, city_property in self.city_info.items():
        #     self.create_node('城市', city_name, city_property['基本情况'])
        # for entity_name, entity_property in {**self.prov_info, **self.city_info}.items():
        #     for property, content in entity_property['基本情况'].items():
        #         if property != '简介':
        #             self.create_other_relation(entity_name, property, content)
        #     self.create_belong_relation(entity_name, entity_property['属于'])
        #     self.create_border_relation(entity_name, entity_property['接壤'])

        self.graph.create(Node("学院", name="人工智能学院"))
        for entity in set(list(self.sai_info.values())):
            self.graph.create(Node("其他", name=entity))
        for prop, entity in self.sai_info.items():
            self.create_sai_relation(prop, entity)

        print("图数据库构建完成！(time={:.2f}s)".format(time.time()-start))


if __name__ == '__main__':
    builder = GraphBuilder()
    builder.pipeline()
    # builder.delete_whole_graph()
