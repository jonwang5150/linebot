
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage,TextMessage,ImageSendMessage
import random

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
                    if '電影' in text:
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

                if message is not None:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=message)
                )
                if image_url is not None:
                    line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=image_url,
                        preview_image_url=image_url))




        return HttpResponse()
    else:
        return HttpResponseBadRequest()


def lotto():
    numbers = sorted(random.sample(range(1, 50), 6))
    result = ' '.join(map(str, numbers))
    n = random.randint(1, 50)
    return f'{result} 特別號:{n}'
