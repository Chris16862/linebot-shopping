# -*- encoding: utf8 -*-
from __future__ import unicode_literals
import os
import sys
from argparse import ArgumentParser
from connection import con
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import SELL as s
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
db = con.cursor()

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)
    for event in events:
        if isinstance(event, JoinEvent) :
            db.execute("INSERT INTO group_list (grid) VALUES (%s)", (event.source.group_id,))
            con.commit()
        if isinstance(event, LeaveEvent):
            db.execute("DELETE FROM group_list WHERE grid='{}'".format(event.source.group_id))
            con.commit()
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.source, SourceUser) :
            continue
        userid = event.source.user_id
        db.execute("SELECT status FROM sell_list WHERE status!='finish' and userid='{}'".format(userid))
        sell_status = db.fetchall()
        if event.message.text=="我要賣東西" or sell_status :
            line_bot_api.reply_message(
                event.reply_token,
                s.get_reply(
                    event,
                    sell_status,
                    userid
                    )
                )
    return 'OK'
   


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()
    app.run(debug=options.debug, port=options.port)
