'''
Author: Derry
Email: drlv@stu.xidian.edu.cn
Date: 2021-01-22 23:15:50
LastEditors: Derry
LastEditTime: 2021-03-13 12:16:36
Description: 问答系统主函数
'''

from question_answering import *
from wave_process import *
from utils import *
import threading


class ChatBot:
    def __init__(self):
        # os.system("neo4j start")
        self.QASystem = QASystem()
        self.speech_in = False
        self.speech_out = False
        print("系统初始化完成！")

    def chat_main(self):
        print('小德：', LoadText('QAcache/welcome.txt'))
        if self.speech_out:
            thread = threading.Thread(target=Play,args=['QAcache/welcome.wav'])
            thread.start()
        while True:
            if self.speech_in:
                Record_common()  # 问题录音
                Speech2Text()  # 录音转文本
                question = LoadText('QAcache/question.txt')  # 加载文本文件
                print('我： ', question)
            else:
                question = input('我：   ')
            if question == '':
                continue
            elif '打开语音' in question:
                self.speech_in = True
                self.speech_out = True
                print('小德：正在打开语音...')
                continue
            elif '关闭语音' in question:
                self.speech_in = False
                self.speech_out = False
                print('小德：正在关闭语音...')
                continue
            elif '再见' in question or '关闭' in question:  # 结束程序
                print('小德：', LoadText('QAcache/goodbye.txt'))
                if self.speech_out:
                    Play('QAcache/goodbye.wav')
                else:
                    time.sleep(1)
                break
            else:
                start = time.time()
                self.QASystem.parse_question(question)
                answer = self.QASystem.query_answer()
                if answer == None:  # 提示重问
                    print('小德： {} (time={:.2f}s)'.format(LoadText(
                        'QAcache/unknow.txt'), time.time()-start))
                    if self.speech_out:
                        thread = threading.Thread(target=Play,args=['QAcache/unknow.wav'])
                        thread.start()
                else:  # 回答问题
                    print('小德： {} (time={:.2f}s)'.format(answer, time.time()-start))
                    if self.speech_out:
                        WriteText('QAcache/answer.txt', answer)
                        Text2Speech()
                        thread = threading.Thread(target=Play,args=['QAcache/answer.wav'])
                        thread.start()

if __name__ == '__main__':
    handler = ChatBot()
    handler.chat_main()
