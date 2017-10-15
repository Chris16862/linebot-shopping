from linebot.models import *
import os
from connection import con
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def get_reply(event, status, userid):
   if not status:
   	s="check"
   	db.execute("INSERT INTO buy_list (userid, status) VALUES (%s, %s)",(userid, s))
   	return TextSendMessage(text="請輸入商品編號:")
   elif status[0][0]="check":
   	buy=event.message,text
   	if number==buy:
   		s="count"
   		db.execute("SELECT price FROM sell_list WHERE status='finish' and id='{}'".format(buy))
   		price=db.fetchall()
   		db.execute("UPDATE buy_list SET id={},status='{}',price='{}' WHERE status='check' and userid='{}'".format(int(buy), s, price, userid))
   		db.execute("SELECT name FROM sell_list WHERE status='finish' and id='{}'".format(buy))
   		name=db.fetchall()
   		db.execute("UPDATE buy_list SET name='{}' WHERE status='count' and userid='{}'".format(name))
   		db.execute("SELECT userid FROM sell_list WHERE status='finish' and id='{}'".format(buy))
   		userid_seller=db.fetchall()
   		db.execute("UPDATE buy_list SET userid_seller='{}' WHERE status='count' and userid='{}'".format(userid_seller, userid))
   		
   		return TextSendMessage(text="請輸入購買數量:")
   	elif status[0][0]="count":
   		s="modify"
   		db.execute("SELECT price FROM sell_list WHERE status='finish' and id='{}'".format(buy))
   		data=db.fetchall()
   		total=data*int(event.message.text)
   		db.execute("UPDATE buy_list SET status='{}' WHERE status='count' and userid='{}'".format(s, userid))
   		db.execute("SELECT name,price FROM buy_list WHERE userid='{}' and status='finish'".format(userid))
            data = db.fetchall()
            name = data[0][0]
            price = data[0][1] 
   		return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否需要更改\n商品名:"+data[0][0]+"\n單價:"+str(data[0][1])+"\n總額:"+str(toal),
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
   	elif status[0][0]="modify" :
        if event.message.text=='Yes' : 
                return TemplateSendMessage(
                    alt_text='Buttons template',
                    template=ButtonsTemplate(
                        title='List',
                        text='請問需要更改哪個項目？',
                        actions=[
                        MessageTemplateAction(
                            label='商品編號',
                            text='商品編號',
                            ),
                        MessageTemplateAction(
                            label='數量',
                            text='數量'
                            )
                        ]
                        )
                    )
        elif event.message.text=='No' :
        		line_bot_api.push_message(
                userid_seller,
                TextSendMessage(text="商品編號#"+str(number)+"\n商品名:"+name+"\n單價:"+str(price)+"\n數量:"+str(amount)+"\n\n"+intro+"\n如需購買請私訊我喔～")
                )