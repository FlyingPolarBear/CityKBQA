'''
Author: Derry
Email: drlv@stu.xidian.edu.cn
Date: 2021-02-15 23:17:13
LastEditors: Derry
LastEditTime: 2021-03-04 21:21:09
Description: 图形界面问答系统主函数
'''

from question_answering import *
from wave_process import *
from utils import *
from tkinter import *
import ctypes
import threading
from PIL import Image, ImageTk

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")


class GUI_Engine(object):
    def __init__(self):
        # 设置超参数和窗口格式
        self.root = Tk()
        self.root.iconbitmap('source/48x48.ico')
        self.root.geometry('600x500')
        self.root.title('小德城市知识问答')
        self.bgcolor = '#dadada'
        self.background = Label(self.root, bg=self.bgcolor)
        self.background.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lb_title = Label(self.root, text='小德城市知识问答', bg=self.bgcolor, fg='#204969',
                              font=('华文新魏', 36, 'bold'), width=20, height=2)
        self.lb_title.place(relx=0, rely=0, relwidth=1, relheight=0.15)

        self.speech_answer = BooleanVar()
        self.dialogs = []
        self.limit_num = 5
        self.root.update()
        self.create_first_dialog()
        self.dialogs.append(LoadText('QAcache/welcome.txt'))
        thread = threading.Thread(target=Play,args=['QAcache/welcome.wav'])
        thread.start()
        self.num = 1
        self.init_botton_bar()

    def init_botton_bar(self):
        lb_entry_icon = Label(self.root)
        photo_icon = ImageTk.PhotoImage(Image.open(
            'source/icon_ques.png').resize((50, 50)))
        lb_entry_icon.config(image=photo_icon,bg=self.bgcolor)
        lb_entry_icon.place(x=0, rely=0.9, width=50,
                            relheight=0.1, anchor='nw')
        # 文本输入栏
        self.entry = Entry(
            self.root, textvariable=StringVar(), font=('华文行楷', 16))
        self.entry.place(
            x=50, rely=0.9, width=self.root.winfo_width()-140, relheight=0.1)
        # 文本输入提交按钮
        self.btn_text = Button(self.root, text='提问',bg=self.bgcolor,
                               command=self.Text_QA, font=('微软雅黑', 12))
        self.btn_text.place(x=self.root.winfo_width()-90,
                            rely=0.9, width=90, relheight=0.1)
        # 语音输入按钮
        self.speech_in_notes = Label(
            self.root, text='欢迎使用语音引擎！',bg=self.bgcolor, font=('华文新魏', 16), height=2)
        self.speech_in_notes.place(x=100, rely=0.8, relheight=0.1, anchor='nw')
        # 语音输入提示栏
        speech_icon = ImageTk.PhotoImage(
            Image.open('source/语音.png').resize((30, 30)))
        self.btn_speech_in = Button(
            self.root, command=self.Speech_QA, image=speech_icon,bg=self.bgcolor)
        self.btn_speech_in.place(x=50, rely=0.82)
        # 语音回答勾选项
        self.btn_speech_out = Checkbutton(
            self.root, text='语音回答',bg=self.bgcolor, variable=self.speech_answer, onvalue=True, offvalue=False, height=2, width=10, font=('微软雅黑', 12))
        self.btn_speech_out.place(
            x=self.root.winfo_width()-140, rely=0.8, relheight=0.1)
        self.root.mainloop()

    def create_first_dialog(self):
        self.lb_icon = [Label(self.root)]
        self.photos = [ImageTk.PhotoImage(Image.open(
            'source/icon_ans.png').resize((50, 50)))]
        self.lb_icon[0].config(image=self.photos[0], bg=self.bgcolor)
        self.lb_name = [
            Label(self.root, text='小德', font=('微软雅黑', 12), bg=self.bgcolor, anchor='w')]
        self.lb_content = [Label(self.root, text=LoadText(
            'QAcache/welcome.txt'), font=('华文行楷', 14), bg=self.bgcolor, anchor='w')]

        self.lb_icon[0].place(x=20, rely=0.16, width=50,
                              relheight=0.1, anchor='nw')
        self.lb_name[0].place(
            x=80, rely=0.16, width=self.root.winfo_width()-100, relheight=0.05, anchor='nw')
        self.lb_content[0].place(x=80, rely=0.21,
                                 width=self.root.winfo_width()-100, relheight=0.05, anchor='nw')

    def create_dialog(self, num):
        if num % 2 == 0:
            align = 'w'
            photo_path = 'source/icon_ans.png'
            x_icon = 20
            x_name_con = 80
            user = '小德'
        else:
            align = 'e'
            photo_path = 'source/icon_ques.png'
            x_icon = self.root.winfo_width()-70
            x_name_con = 20
            user = '我'
        self.lb_icon.append(Label(self.root))
        self.photos.append(ImageTk.PhotoImage(
            Image.open(photo_path).resize((50, 50))))
        self.lb_icon[num].config(image=self.photos[num], bg=self.bgcolor)
        self.lb_content.append(
            Label(self.root, text=self.dialogs[num], font=('华文行楷', 14), bg=self.bgcolor, anchor=align))
        self.lb_name.append(
            Label(self.root, text=user, font=('微软雅黑', 12), bg=self.bgcolor, anchor=align))
        if num >= 5:
            des_num = num-5
            self.lb_icon[des_num].destroy()
            self.lb_content[des_num].destroy()
            self.lb_name[des_num].destroy()
            for i in range(4):
                rel_num = num-4+i
                if rel_num % 2 == 0:
                    x_icon0 = 20
                    x_name_con0 = 80
                else:
                    x_icon0 = self.root.winfo_width()-70
                    x_name_con0 = 20
                self.lb_icon[num-4+i].place(x=x_icon0,
                                            rely=0.16+i*0.13, width=50, relheight=0.1)
                self.lb_name[num-4+i].place(x=x_name_con0, rely=0.16 +
                                            i*0.13, width=self.root.winfo_width()-100, relheight=0.05)
                self.lb_content[num-4+i].place(x=x_name_con0, rely=0.21 +
                                               i*0.13, width=self.root.winfo_width()-100, relheight=0.05)
                self.lb_icon[num].place(
                    x=x_icon, rely=0.16+4*0.13, width=50, relheight=0.1)
                self.lb_name[num].place(
                    x=x_name_con, rely=0.16+4*0.13, width=self.root.winfo_width()-100, relheight=0.05)
                self.lb_content[num].place(
                    x=x_name_con, rely=0.21+4*0.13, width=self.root.winfo_width()-100, relheight=0.05)
        else:
            self.lb_icon[num].place(
                x=x_icon, rely=0.16+num*0.13, width=50, relheight=0.1)
            self.lb_name[num].place(
                x=x_name_con, rely=0.16+num*0.13, width=self.root.winfo_width()-100, relheight=0.05)
            self.lb_content[num].place(
                x=x_name_con, rely=0.21+num*0.13, width=self.root.winfo_width()-100, relheight=0.05)

    def Text_QA(self):
        WriteText('QAcache/question.txt', self.entry.get())
        self.Answering()

    def Speech_QA(self):
        Record(self)  # 问题录音
        Speech2Text()  # 录音转文本
        self.Answering()

    def Answering(self):
        question = LoadText('QAcache/question.txt')  # 加载文本文件
        self.dialogs.append(question)
        self.create_dialog(self.num)
        self.root.update()
        self.num += 1

        if '再见' in question or '关闭' in question:  # 结束程序
            self.dialogs.append(LoadText('QAcache/goodbye.txt'))
            self.create_dialog(self.num)
            self.root.update()
            if self.speech_answer.get():
                thread = threading.Thread(target=Play,args=["QAcache/goodbye.wav"])
                thread.start()
                thread.join()
            else:
                time.sleep(1)
            self.root.destroy()
        else:
            xiaode.parse_question(question)
            answer = xiaode.query_answer()
            if answer == None:  # 提示重问
                self.dialogs.append(LoadText('QAcache/unknow.txt'))
                self.create_dialog(self.num)
                if self.speech_answer.get():
                    thread = threading.Thread(target=Play,args=['QAcache/unknow.wav'])
                    thread.start()
            else:  # 回答问题
                self.dialogs.append(answer)
                self.create_dialog(self.num)
                WriteText('QAcache/answer.txt', answer)
                if self.speech_answer.get():
                    Text2Speech()
                    thread = threading.Thread(target=Play,args=['QAcache/answer.wav'])
                    thread.start()
            self.root.update()
        self.num += 1


if __name__ == "__main__":
    xiaode = QASystem()
    xiaode_gui = GUI_Engine()
