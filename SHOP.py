# -*- encoding: utf8 -*-
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
from paramiko import SSHClient,AutoAddPolicy
from scp import SCPClient

app = Flask(__name__)
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
        if isinstance(event.message, ImageMessage) :
            os.system("touch test.jpg")
            message_content = line_bot_api.get_message_content(event.message.id)
            with open('test.jpg', 'wb') as fd:
                for chunk in message_content.iter_content():
                    fd.write(chunk)
            server = "cscc.hsexpert.net"
            port = 22
            user = "apie0419"
            password = "a19970419"
            client = SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(server, port, user, password)
            scp = SCPClient(client.get_transport())
            scp.put('test.jpg','public_html/test.jpg')
            scp.close()
            line_bot_api.reply_message(
                event.reply_token,
                ImageMessage(
                    originalContentUrl="https://web-stu.tkucs.cc/404411240/test.jpg",
                    previewImageUrl="https://web-stu.tkucs.cc/404411240/test.jpg"
                )
            )
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
        if event.message.text=="/Sell" or sell_status :
            line_bot_api.reply_message(
                event.reply_token,
                s.get_reply(
                    event,
                    sell_status,
                    userid
                    )
                )
        elif event.message.text=="/Buy" :
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(
                    text="不好意思,此功能尚未開放,敬請期待"
                    )
                )
        elif event.message.text=='/BuyList' :
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(
                    text="不好意思,此功能尚未開放,敬請期待"
                    )
                )
        elif event.message.text=='/SellList' :
             line_bot_api.reply_message(
                event.reply_token,
                TextMessage(
                    text="不好意思,此功能尚未開放,敬請期待"
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
