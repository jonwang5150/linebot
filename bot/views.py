
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage,TextMessage,ImageSendMessage
import random
from bs4 import BeautifulSoup
import requests
import numpy as np


line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parse = WebhookParser(settings.LINE_CHANNEL_SECRET)

def index(requests):
    return HttpResponse("<h1>LineBot APP</h1>")


@csrf_exempt
def callback(request):
    words=['早安~你好,今天好嗎?','天氣很不錯!','我要去上班~','快中午了,肚子好餓?',
    '再說一次']
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parse.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        for event in events:
            if isinstance(event, MessageEvent):
                if isinstance(event.message,TextMessage):
                    message,image_url=None,None
                    text=event.message.text
                    print(text)
                    if '大樂透'==text:
                        message=get_biglotto()
                    elif '電影' in text:
                        message='https://movies.yahoo.com.tw/'
                    elif '台中捷運' in text:
                        image_url='https://upload.wikimedia.org/wikipedia/commons/c/c0/Taichung_MRT_Planning_Route_Map.jpg'
                    elif '台北捷運' in text:
                        message='https://www.travel.taipei/Content/images/static/travel-tips/metrotaipeimap.jpg'
                    elif '早安' in text:
                        message='早安你好!'
                    elif '樂透' in text:
                        message=lotto()
                    else:
                        message=random.choice(words)

                else:
                    message='無法解析'
                
                messageObject=TextSendMessage(text=message) if message is not None else \
                    ImageSendMessage(original_content_url=image_url,preview_image_url=image_url)
                
                line_bot_api.reply_message(event.reply_token,messageObject)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()


def lotto():
    numbers = sorted(random.sample(range(1, 50), 6))
    result = ' '.join(map(str, numbers))
    n = random.randint(1, 50)
    return f'{result} 特別號:{n}'



def get_biglotto():
    url='https://www.taiwanlottery.com.tw/lotto/Lotto649/history.aspx'
    resp=requests.get(url)
    soup=BeautifulSoup(resp.text,'lxml')
    trs=soup.find('table',class_='table_org td_hm').find_all('tr')
    numbers=[td.text.strip() for td in trs[4].find_all('td')[1:]]
    numbers=' '.join(numbers[:-1])+'特別號'+numbers[-1]
    data1=[td.text.strip() for td in trs[0].find_all('td')]
    data2=[td.text.strip() for td in trs[1].find_all('td')]
    data=list(zip(data1,data2))
    title=':'.join(np.array(data).reshape(10))
    result=f'{title}\n{numbers}'
    
    return result