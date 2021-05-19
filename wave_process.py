'''
Author: Derry
Email: drlv@stu.xidian.edu.cn
Date: 2021-01-20 21:23:22
LastEditors: Derry
LastEditTime: 2021-05-19 11:21:27
Description: 云语音任务工具箱

语音听写流式 WebAPI 接口调用示例 接口文档（必看）：https://doc.xfyun.cn/rest_api/语音听写（流式版）.html
webapi 听写服务参考帖子（必看）：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=38947&extra=
热词使用方式：登陆开放平台https://www.xfyun.cn/后，找到控制台--我的应用---语音听写（流式）---服务管理--个性化热词，设置热词
注意：热词只能在识别的时候会增加热词的识别权重，需要注意的是增加相应词条的识别率，但并不是绝对的，具体效果以您测试为准。
方言试用方法：登陆开放平台https://www.xfyun.cn/后，找到控制台--我的应用---语音听写（流式）---服务管理--识别语种列表
可添加语种或方言，添加后会显示该方言的参数值
错误码链接：https://www.xfyun.cn/document/error-code
'''

import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import os
import ssl
import time
import wave
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import pyaudio
import websocket

from utils import *


def Record(gui_engine, filename='QAcache/question.wav', CHUNK=1024, FORMAT=pyaudio.paInt16, CHANNELS=1, RATE=16000, RECORD_SECONDS=5):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)
    frames = []
    for i in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        if i % int(RATE / CHUNK) == 0:
            notes = f"请说出您的问题... （剩余{RECORD_SECONDS-int(i/(RATE / CHUNK))-1}秒）"
            gui_engine.speech_in_notes.config(text=notes)
            gui_engine.root.update()
        gui_engine.speech_in_notes.config(text='录音完毕！欢迎继续使用')
    print(' '*30, end='\r')
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def Record_common(filename='QAcache/question.wav', CHUNK=1024, FORMAT=pyaudio.paInt16, CHANNELS=1, RATE=16000, RECORD_SECONDS=5):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)
    frames = []
    for i in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        if i % int(RATE / CHUNK) == 0:
            print("请说出您的问题... （剩余{}秒）".format(
                RECORD_SECONDS-int(i/(RATE / CHUNK))-1), end='\r')
    print(' '*30, end='\r')
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def Play(filename='QAcache/startmusic.wav', CHUNK=1024):
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(CHUNK)
    while data != b'':
        stream.write(data)
        data = wf.readframes(CHUNK)
    stream.stop_stream()
    stream.close()
    p.terminate()


class Speech2Text_Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, AudioFile):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile
        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn",
                             "accent": "mandarin", "vinfo": 1, "vad_eos": 10000}

    # 生成url
    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(
            signature_sha).decode(encoding='utf-8')
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(
            authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url


class Speech2Text_Status(object):
    # 收到websocket消息的处理
    def on_message(ws, message):
        try:
            code = json.loads(message)["code"]
            sid = json.loads(message)["sid"]
            if code != 0:
                errMsg = json.loads(message)["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                data = json.loads(message)["data"]["result"]["ws"]
                # print(json.loads(message))
                result = ""
                for i in data:
                    for w in i["cw"]:
                        result += w["w"]
                # print("sid:%s call success!,data is:%s" %
                #       (sid, json.dumps(data, ensure_ascii=False)))
                AddText('QAcache/question.txt', result)
        except Exception as e:
            print("receive msg,but parse exception:", e)

    # 收到websocket错误的处理
    def on_error(ws, error):
        print("### error:", error)

    # 收到websocket关闭的处理
    def on_close(ws):
        pass
        # print("### closed ###")

    # 收到websocket连接建立的处理
    def on_open(ws):
        wsParam = Speech2Text_Ws_Param(APPID='6006eb88', APISecret='e886222733683273551f890cf5501dd8',
                                       APIKey='2c3e3bc97c22cb052b00787b81db4709',
                                       AudioFile='QAcache/question.wav')

        def run(*args):
            STATUS_FIRST_FRAME = 0  # 第一帧的标识
            STATUS_CONTINUE_FRAME = 1  # 中间帧标识
            STATUS_LAST_FRAME = 2  # 最后一帧的标识
            frameSize = 8000  # 每一帧的音频大小
            intervel = 0.04  # 发送音频间隔(单位:s)
            status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧
            with open(wsParam.AudioFile, "rb") as fp:
                while True:
                    buf = fp.read(frameSize)
                    # 文件结束
                    if not buf:
                        status = STATUS_LAST_FRAME
                    # 第一帧处理
                    # 发送第一帧音频，带business 参数
                    # appid 必须带上，只需第一帧发送
                    if status == STATUS_FIRST_FRAME:
                        d = {"common": wsParam.CommonArgs,
                             "business": wsParam.BusinessArgs,
                             "data": {"status": 0, "format": "audio/L16;rate=16000",
                                      "audio": str(base64.b64encode(buf), 'utf-8'),
                                      "encoding": "raw"}}
                        d = json.dumps(d)
                        ws.send(d)
                        status = STATUS_CONTINUE_FRAME
                    # 中间帧处理
                    elif status == STATUS_CONTINUE_FRAME:
                        d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                      "audio": str(base64.b64encode(buf), 'utf-8'),
                                      "encoding": "raw"}}
                        ws.send(json.dumps(d))
                    # 最后一帧处理
                    elif status == STATUS_LAST_FRAME:
                        d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                      "audio": str(base64.b64encode(buf), 'utf-8'),
                                      "encoding": "raw"}}
                        ws.send(json.dumps(d))
                        time.sleep(1)
                        break
                    # 模拟音频采样间隔
                    time.sleep(intervel)
            ws.close()
        thread.start_new_thread(run, ())


def Speech2Text():
    WriteText('QAcache/question.txt','')
    wsParam = Speech2Text_Ws_Param(APPID='6006eb88', APISecret='e886222733683273551f890cf5501dd8',
                                   APIKey='2c3e3bc97c22cb052b00787b81db4709', AudioFile='QAcache/question.wav')
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=Speech2Text_Status.on_message,
                                on_error=Speech2Text_Status.on_error, on_close=Speech2Text_Status.on_close)
    ws.on_open = Speech2Text_Status.on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


class Text2Speech_Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {
            "aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8"}
        self.Data = {"status": 2, "text": str(
            base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
        # 使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        #self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(
            signature_sha).decode(encoding='utf-8')
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(
            authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url


class Text2Speech_Status(object):
    def on_message(ws, message):
        try:
            message = json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            # print(message)
            if status == 2:
                # print("ws is closed")
                ws.close()
            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                with open('QAcache/answer.pcm', 'ab') as f:
                    f.write(audio)
        except Exception as e:
            print("receive msg, but parse exception:", e)

    def on_error(ws, error):  # 收到websocket错误的处理
        print("### error:", error)

    def on_close(ws):  # 收到websocket关闭的处理
        pass
        # print("### closed ###")

    def on_open(ws):  # 收到websocket连接建立的处理
        def run(*args):
            wsParam = Text2Speech_Ws_Param(APPID='6006eb88', APISecret='e886222733683273551f890cf5501dd8',
                                           APIKey='2c3e3bc97c22cb052b00787b81db4709',
                                           Text=LoadText('QAcache/answer.txt'))
            d = {"common": wsParam.CommonArgs,
                 "business": wsParam.BusinessArgs,
                 "data": wsParam.Data,
                 }
            d = json.dumps(d)
            # print("------>开始发送文本数据")
            ws.send(d)
            if os.path.exists('QAcache/answer.pcm'):
                os.remove('QAcache/answer.pcm')
        thread.start_new_thread(run, ())


def Text2Speech(file="QAcache/answer"):
    wsParam = Text2Speech_Ws_Param(APPID='6006eb88', APISecret='e886222733683273551f890cf5501dd8',
                                   APIKey='2c3e3bc97c22cb052b00787b81db4709', Text=LoadText(file+'.txt'))
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=Text2Speech_Status.on_message,
                                on_error=Text2Speech_Status.on_error, on_close=Text2Speech_Status.on_close)
    ws.on_open = Text2Speech_Status.on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    with open(file+".pcm", 'rb') as pcmfile:
        pcmdata = pcmfile.read()
    with wave.open(file+".wav", 'wb') as wavfile:
        wavfile.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
        wavfile.writeframes(pcmdata)


if __name__ == "__main__":
    Record_common()  # 问题录音
    Speech2Text()  # 录音转文本
    question = LoadText('QAcache/question.txt')  # 加载文本文件
    print('我： ', question)
    Text2Speech()
    Play(filename='QAcache/answer.wav', CHUNK=1024)
