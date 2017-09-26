from __future__ import unicode_literals

#import jieba
#from pandas import Series, DataFrame
#import pandas as pd 
import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)
#jieba.load_userdict('moe.dict')

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    global tags
    mo_name=[]
    mo_price=[]
    mo_style=[]
    mo_intro=[]
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        print(tags)
        if tags=="商品名":
            mo_name.append(event.message.text)
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入價錢:")
            )
            tags="價錢"
        if tags=="價錢":
            mo_price.append(event.message.text)
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入規格:")
            )
            tags="規格"
        if tags=="規格":
            mo_style.append(event.message.text)
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入介紹或優惠:")
            )
            tags="介紹"
        if tags=="介紹":
            mo_intro.append(event.message.text)
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="輸入完畢，請確認內容:\n商品名:"+mo_name+"\n價錢:"+mo_price+"\n規格:"+mo_style+"\n介紹及優惠:"+mo_intro)
            )

        if event.message.text=="我要賣東西":
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入商品名:")
            )
            tags="商品名"
            
    
    return 'OK'
   


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()
    app.run(debug=options.debug, port=options.port)
