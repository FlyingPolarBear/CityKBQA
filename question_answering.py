'''
Author: Derry
Email: drlv@stu.xidian.edu.cn
Date: 2021-02-13 11:28:37
LastEditors: Derry
LastEditTime: 2021-05-06 16:24:57
Description: 问答系统引擎
'''

import logging

import ahocorasick
import jieba
import jieba.posseg as pseg
import Levenshtein
import numpy as np
from py2neo import Graph
from scipy.spatial import distance

from utils import *

jieba.setLogLevel(logging.INFO)


class QASystem(object):
    def __init__(self):
        self.relation_words = ("属于", "包含", "接壤")
        self.city_prop_path = 'data/final/城市属性及别称.txt'
        self.prov_prop_path = 'data/final/省份属性及别称.txt'
        self.city_name_path = 'data/final/城市列表及别称.txt'
        self.prov_name_path = 'data/final/省份列表及别称.txt'
        self.w2v_path = 'D:/word2vec/renmin.w2v'
        self.sai_prop, self.sai_tail = load_sai_info(
            'data/added_knowledge/sai_data.txt')
        self.graph = Graph(host="localhost", http_port=7474,
                           user="neo4j", password="456123")
        self.prop_acauto, self.prop_list = self.build_acauto(
            self.city_prop_path, self.prov_prop_path, [[prop] for prop in self.sai_prop])
        self.name_acauto, self.name_list = self.build_acauto(
            self.city_name_path, self.prov_name_path, [['人工智能学院', 'AI院', '智能院']])
        self.word2vec = self.load_word2vec()
        self.stopwords = set(
            load_list("data/stopwords_list/hit_stopwords.txt"))
        print("系统启动完毕！")

    def build_acauto(self, city_path, prov_path, other_list):
        city_list = [city.split()
                     for city in LoadText(city_path).split('\n')]
        prov_list = [prov.split()
                     for prov in LoadText(prov_path).split('\n')]
        actree = ahocorasick.Automaton()
        entity_list = city_list+prov_list+other_list
        for index, props in enumerate(entity_list):
            for prop in props:
                actree.add_word(prop, (index, props[0]))
                jieba.add_word(prop)
        actree.make_automaton()
        return actree, entity_list

    def load_word2vec(self):
        print("加载词向量中...")
        word2vec = {}
        with open(self.w2v_path, encoding='utf-8') as f:
            for line in f:
                line = line.replace("\u3000", "").strip().split()
                word = line[0]
                vec = line[1:]
                word2vec[word] = np.array(vec, dtype=np.float32)
        print("加载词向量完成！")
        return word2vec

    def compute_similarity(self, word1, word2, alpha=0.5):  # 计算相似度
        maxlen = max(len(word1), len(word2))
        Leven_similarity = (maxlen - Levenshtein.distance(word1, word2))/maxlen
        if word1 in self.word2vec.keys() and word2 in self.word2vec.keys():
            cos_similarity = 1 - \
                distance.cosine(self.word2vec[word1], self.word2vec[word2])
        else:
            cos_similarity = Leven_similarity
        return alpha*cos_similarity+(1-alpha)*Leven_similarity

    def find_most_similar(self, candidate_words):  # 寻找最相似的词
        word2similarity = {}
        for word in self.sentence_words:
            for candidate_word in candidate_words:
                word2similarity[word+' '+candidate_word] = round(
                    self.compute_similarity(word, candidate_word), 2)
        similarity, link = max(
            zip(word2similarity.values(), word2similarity.keys()))
        predicate, sim_word = link.split()
        # print('选中词：', predicate, '| 相似词：', sim_word,
        #       '| 相似度：', similarity, end=' ')
        return sim_word

    def named_entity_recognition(self, question):  # 命名实体识别
        entity_parse = self.name_acauto.iter(question)
        named_entity = list(set([entity[1][1] for entity in entity_parse]))
        # print("候选实体：", named_entity, end=' ')
        if len(named_entity) == 1:
            return named_entity[0]
        elif len(named_entity) < 1:
            named_entity = [name[0]
                            for name in self.name_list if name[0] not in self.stopwords]
        return self.find_most_similar(named_entity)

    def relation_extraction(self, question):  # 属性映射
        prop_parse = self.prop_acauto.iter(question)
        prop_words = list(set([prop[1][1] for prop in prop_parse]))
        # print('候选属性:', prop_words, end=' ')
        if len(prop_words) == 1:
            return prop_words[0]
        elif len(prop_words) < 1:
            return ''
        else:
            return self.find_most_similar(prop_words)

    def parse_question(self, question):
        self.sentence_words = list(jieba.cut(question)) # 精确模式
        # self.sentence_words = list(jieba.cut_for_search(question)) # 搜索引擎模式
        # self.sentence_words_flags = [(w.word, w.flag)
        #                              for w in pseg.cut(question)]
        # self.sentence_words = [s[0] for s in self.sentence_words_flags]
        # self.sentence_flags = [s[1] for s in self.sentence_words_flags]
        self.question_factor = {}
        self.question_factor['entity'] = self.named_entity_recognition(
            question)
        self.question_factor['prop'] = self.relation_extraction(question)
        if not len(self.question_factor['prop']):
            self.question_factor['link'] = self.find_most_similar(
                self.relation_words)

    def query_answer(self):
        query = ''
        self.answers = None
        if len(self.question_factor['entity']):
            if len(self.question_factor['prop']):
                if self.question_factor['prop'] == '简介':
                    query = f"match (e) " \
                        f"where e.name='{self.question_factor['entity']}' " \
                        f"return e.introduction"
                else:
                    query = f"match (a)-[r:{self.question_factor['prop']}]->(b) " \
                        f"where a.name='{self.question_factor['entity']}' " \
                        f"return b.name"
                self.answers = self.question_factor['entity'] + \
                    '的'+self.question_factor['prop']+'为'
            elif self.question_factor['link'] == '属于':
                query = f"match (a)-[r:{'属于'}]->(b) " \
                    f"where a.name='{self.question_factor['entity']}' " \
                    f"return b.name"
                self.answers = self.question_factor['entity'] + \
                    self.question_factor['link']
            elif self.question_factor['link'] == '接壤':
                query = f"match (a)-[r:{'接壤'}]-(b) " \
                    f"where a.name='{self.question_factor['entity']}' " \
                    f"return b.name"
                self.answers = self.question_factor['entity'] + \
                    self.question_factor['link']
            elif self.question_factor['link'] == '包含':
                query = f"match (a)-[r:{'属于'}]->(b) " \
                    f"where b.name='{self.question_factor['entity']}' " \
                    f"return a.name"
                self.answers = self.question_factor['entity']+'包含'

        if len(query):
            answers = []
            for answer in self.graph.run(query).data():
                answers.append(list(answer.values())[0])
            if len(answers) == 0 or not answers[0]:
                self.answers = None
            else:
                self.answers += '、'.join(answers)
        return self.answers

    def main(self):
        test_question_stream = load_list('data/test_question.txt')
        # while True:
        #     question = input('问题：')
        for question in test_question_stream:
            if question == '退出' or question.startswith('q'):
                break
            print('问题：{}'.format(question))
            self.parse_question(question)
            answers = self.query_answer()
            if answers:
                print('回答：{}'.format(answers))
            else:
                print('回答：抱歉，没有找到答案')


if __name__ == '__main__':
    qa = QASystem()
    qa.main()
