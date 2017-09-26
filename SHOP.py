from __future__ import unicode_literals

#import jieba
from pandas import Series, DataFrame
import pandas as pd 
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
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

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
   		if event.message.text=="我要賣東西":
   			  buttons_template = TemplateSendMessage(
            	alt_text='開始玩 template',
            	template=ButtonsTemplate(
                title='選擇類型',
                text='請選擇',
                thumbnail_image_url='https://i.imgur.com/xQF5dZT.jpg',
                actions=[
                    MessageTemplateAction(
                        label='商品名',
                        text='商品名'
                    ),
                    MessageTemplateAction(
                        label='價錢',
                        text='價錢'
                    ),
                    MessageTemplateAction(
                        label='規格',
                        text='規格'
                    ),
                    MessageTemplateAction(
                        label='介紹',
                        text='介紹'
                    )
                ]
            )
        )
	line_bot_api.reply_message(event.reply_token, buttons_template)











        	line_bot_api.reply_message(
            	event.reply_token,
            	TextSendMessage(text="請輸入商品名:")
        	)	
       
        '''if event.message.text=="我要賣東西":
        	line_bot_api.reply_message(
            	event.reply_token,
            	TextSendMessage(text="請輸入你要賣的東西(依照以下範例):\n依序打入:商品名 規格 價格 介紹\n範例:蘋果 200g 20元 新鮮甜美的蘋果喔!!")
        	)
        com_info=event.message.text
        print(com_info)

        if event.message.text=="我要買東西":
        	line_bot_api.reply_message(
            	event.reply_token,
            	TextSendMessage(text="請輸入商品名:")
        	)
        if event.message.text'''
    return 'OK'
   


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()
    app.run(debug=options.debug, port=options.port)
