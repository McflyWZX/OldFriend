'''
Author: iflytek、Mcfly coolmcfly@qq.com
Date: 2025-02-26 21:09:17
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-03-30 16:21:11
fileName: \GitClone\OldFriend\XunFeiTTS.py
Description: 基于讯飞官方demo实现讯飞在线TTS client
本demo测试时运行的环境为：Windows + Python3.7
本demo测试成功运行时所安装的第三方库及其版本如下：
 cffi==1.12.3
 gevent==1.4.0
 greenlet==0.4.15
 pycparser==2.19
 six==1.12.0
 websocket==0.2.1
 websocket-client==0.56.0
 合成小语种需要传输小语种文本、使用小语种发音人vcn、tte=unicode以及修改文本编码方式
错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
'''
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os
from pydub import AudioSegment
from pydub.playback import play
import io
from TTS_service import TTS_service


STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class XunFeiTTS(TTS_service, object):
    # 初始化
    def __init__(self):
        self.APPID = '05745f43'
        self.APIKey = '7d21bdfa0414f25762c40b8c04ac251b'
        self.APISecret = 'MTA1Yzc1ODJjZTMwYjIyMjMyNDE0NDg2'

    def tts(self, text: str, ttsPath: str, fileName: str):
        super().tts(text, ttsPath, fileName)
        self.__setArgs(text)
        websocket.enableTrace(False)
        wsUrl = self.__create_url()
        ws = websocket.WebSocketApp(
            wsUrl, 
            on_message=lambda ws, message: self.__on_message(ws, message), 
            on_error=lambda ws, error: self.__on_error(ws, error), 
            on_close=lambda ws: self.__on_close(ws),
            on_open=lambda ws: self.__on_open(ws)
        )
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def __setArgs(self, text: str):
        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "lame", "sfl": 1, "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8"}
        self.Data = {"status": 2, "text": str(base64.b64encode(text.encode('utf-8')), "UTF8")}
        #使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        #self.Data = {"status": 2, "text": str(base64.b64encode(text.encode('utf-16')), "UTF8")}

    # 生成url
    def __create_url(self):
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
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
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

    def __on_message(self, ws, message):
        try:
            message =json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            # print(message)
            if status == 2:
                print("ws is closed")
                ws.close()
            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                directory = os.path.dirname(self.ttsPath)
                os.makedirs(directory, exist_ok=True)
                with open(self.ttsPath + self.fileName, 'ab') as f:
                    f.write(audio)
            

        except Exception as e:
            print("receive msg,but parse exception:", e)

    # 收到websocket错误的处理
    def __on_error(self, ws, error):
        print("### error:", error)


    # 收到websocket关闭的处理
    def __on_close(self, ws):
        print("### closed ###")


    # 收到websocket连接建立的处理
    def __on_open(self, ws):
        def run(*args):
            d = {"common": self.CommonArgs,
                "business": self.BusinessArgs,
                "data": self.Data,
                }
            d = json.dumps(d)
            print("------>开始发送文本数据")
            ws.send(d)
            if os.path.exists(self.ttsPath + self.fileName):
                os.remove(self.ttsPath + self.fileName)

        thread.start_new_thread(run, ())


if __name__ == "__main__":
    ttsService = XunFeiTTS('ttsFile/')
    ttsService.tts('陈翔6点半', 'test.mp3')


