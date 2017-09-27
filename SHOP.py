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
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        userid = event.source.user_id
        db.execute("SELECT status FROM sell_list WHERE status!='finish' and userid='{}'".format(userid))
        status = db.fetchall()
        if event.message.text=="我要賣東西" and not status :
            s = "enter_name"
            db.execute("INSERT INTO sell_list (userid, status) VALUES (%s, %s)",(userid, s))
            con.commit()
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入商品名:")
            )
        elif status[0][0]=="enter_name":
            s = "enter_price"
            SQL = "UPDATE sell_list SET name='{}',status='{}' WHERE status='enter_name' and userid='{}';".format(event.message.text, s, userid)
            db.execute(SQL)
            con.commit()
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入單價:")
            )
        elif status[0][0]=="enter_price":
            s = "enter_amount"
            db.execute("UPDATE sell_list SET price={},status='{}' WHERE status='enter_price' and userid='{}'".format(int(event.message.text), s, userid))
            con.commit()
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入提供數量:")
            )
        elif status[0][0]=="enter_amount":
            s = "enter_intro"
            db.execute("UPDATE sell_list SET amount={},status='{}' WHERE status='enter_amount' and userid='{}'".format(int(event.message.text), s, userid))
            con.commit()
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入介紹或優惠:")
            )
        elif status[0][0]=="enter_intro":
            s = "modify"
            db.execute("SELECT name,price,amount FROM sell_list WHERE status='enter_intro' and userid='{}'".format(userid))
            data = db.fetchall()
            db.execute("UPDATE sell_list SET intro='{}',status='{}' WHERE status='enter_intro' and userid='{}'".format(event.message.text, s, userid))
            con.commit()
            line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text="輸入完畢，請確認內容是否需要更改\n商品名:"+data[0][0]+"\n單價:"+str(data[0][1])+"\n數量:"+str(data[0][2])+"\n介紹及優惠:"+event.message.text,
                    actions=[
                    MessageTemplateAction(
                        label='Yes',
                        text='Yes',
                        ),
                    MessageTemplateAction(
                        label='No',
                        text='No'
                        )
                    ]
                    )
                )
            )
        elif status[0][0]=="modify_name":
            db.execute("SELECT price,amount,intro FROM sell_list WHERE status='enter_intro' and userid='{}'".format(userid))
            data = db.fetchall()
            s = "modify"
            SQL = "UPDATE sell_list SET name='{}',status='{}' WHERE status='enter_name' and userid='{}';".format(event.message.text, s, userid)
            db.execute(SQL)
            con.commit()
            line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text="輸入完畢，請確認內容是否需要更改\n商品名:"+event.message.text+"\n單價:"+str(data[0][0])+"\n數量:"+str(data[0][1])+"\n介紹及優惠:"+data[0][2],
                    actions=[
                    MessageTemplateAction(
                        label='Yes',
                        text='Yes',
                        ),
                    MessageTemplateAction(
                        label='No',
                        text='No'
                        )
                    ]
                    )
                )
            )
        elif status[0][0]=="modify_price":
            db.execute("SELECT name,amount,intro FROM sell_list WHERE status='enter_intro' and userid='{}'".format(userid))
            data = db.fetchall()
            s = "modify"
            db.execute("UPDATE sell_list SET price={},status='{}' WHERE status='enter_price' and userid='{}'".format(int(event.message.text), s, userid))
            con.commit()
            line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text="輸入完畢，請確認內容是否需要更改\n商品名:"+data[0][0]+"\n單價:"+event.message.text+"\n數量:"+str(data[0][1])+"\n介紹及優惠:"+data[0][2],
                    actions=[
                    MessageTemplateAction(
                        label='Yes',
                        text='Yes',
                        ),
                    MessageTemplateAction(
                        label='No',
                        text='No'
                        )
                    ]
                    )
                )
            )
        elif status[0][0]=="modify_amount":
            db.execute("SELECT name,price,intro FROM sell_list WHERE status='enter_intro' and userid='{}'".format(userid))
            data = db.fetchall()
            s = "modify"
            db.execute("UPDATE sell_list SET amount={},status='{}' WHERE status='enter_amount' and userid='{}'".format(int(event.message.text), s, userid))
            con.commit()
            line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text="輸入完畢，請確認內容是否需要更改\n商品名:"+data[0][0]+"\n單價:"+str(data[0][1])+"\n數量:"+event.message.text+"\n介紹及優惠:"+data[0][2],
                    actions=[
                    MessageTemplateAction(
                        label='Yes',
                        text='Yes',
                        ),
                    MessageTemplateAction(
                        label='No',
                        text='No'
                        )
                    ]
                    )
                )
            )
        elif status[0][0]=="modify_intro":
            db.execute("SELECT name,price,amount FROM sell_list WHERE status='enter_intro' and userid='{}'".format(userid))
            data = db.fetchall()
            s = "modify"
            db.execute("UPDATE sell_list SET intro='{}',status='{}' WHERE status='enter_amount' and userid='{}'".format(event.message.text, s, userid))
            con.commit()
            line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text="輸入完畢，請確認內容是否需要更改\n商品名:"+data[0][0]+"\n單價:"+str(data[0][1])+"\n數量:"+data[0][2]+"\n介紹及優惠:"+event.message.text,
                    actions=[
                    MessageTemplateAction(
                        label='Yes',
                        text='Yes',
                        ),
                    MessageTemplateAction(
                        label='No',
                        text='No'
                        )
                    ]
                    )
                )
            )
        elif status[0][0]=="modify" :
            if event.message.text=='Yes' : 
                line_bot_api.reply_message(
                    event.reply_token,
                    TemplateSendMessage(
                        alt_text='Buttons template',
                        template=ButtonsTemplate(
                            title='List',
                            text='請問需要更改哪個項目？',
                            actions=[
                            MessageTemplateAction(
                                label='商品名',
                                text='商品名',
                                ),
                            MessageTemplateAction(
                                label='單價',
                                text='單價'
                                ),
                            MessageTemplateAction(
                                label='數量',
                                text='數量'
                                ),
                            MessageTemplateAction(
                                label='介紹及優惠',
                                text='介紹及優惠'
                                )
                            ]
                            )
                        )
                    )
                    
            elif event.message.text=='No' :
                s = 'finish'
                db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
                con.commit()
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="商品新增完成")
                )
            elif event.message.text=="商品名" :
                s = "modify_name"
                db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
                con.commit()
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入商品名:")
                )
            elif event.message.text=="單價" :
                s = "modify_price"
                db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
                con.commit()
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入單價:")
                )
            elif event.message.text=="數量" :
                s = "modify_amount"
                db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
                con.commit()
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入數量:")
                )
            elif event.message.text=="介紹及優惠":
                s = "modify_intro"
                db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
                con.commit()
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入介紹及優惠:")
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
