version = "1.0.2"

#LINEBOT
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError , LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage ,StickerMessage,
)

#pycatchがウザいので生成停止
from sys import dont_write_bytecode;dont_write_bytecode = True


class LINEBOT:
    def __init__(self,user_data):

        self.user_id = user_data["LINE_Userid"]
        self.access_token = user_data["LINE_Access_Token"]
        self.channel_secret = user_data["LINE_Channel_Secret"]
        self.Notify_Token = user_data["LINE_Notify_Token"]

        self.line_bot_api = LineBotApi(self.access_token)
        self.handler = WebhookHandler(self.channel_secret)
        self.Message_Event = MessageEvent
        self.Text_Message = TextMessage

    #notify送信メソッド
    def Notify(self,message:str):#メッセージのみ
        import requests
        Token = self.Notify_Token
        API = 'https://notify-api.line.me/api/notify'
        payload = {"message": f"Notify\n{message}"}
        headers = {'Authorization': f'Bearer {Token}'}
        requests.post(API, data=payload, headers=headers)

        print(f"via Notify:{message}")

 #送信メソッド
    def send_message(self,message,to="None"):
        
        


        #送信先を書かなかった場合，デフォルトに戻す
        if(to == "None"):
            to = self.user_id

        #送る
        if(to == "Notify"):
            self.Notify(message)

        else:
            try:
                self.line_bot_api.push_message(to,TextSendMessage(message))
                print(f"via API:{message}")
            
            except LineBotApiError as err:
                if(err.status_code == 429):
                    #429エラー=無料分上限に到達してしまった
                    self.Notify("Error Code:429")
                    self.Notify(message)
                    print(f"Error :429")
                
                else:
                    self.Notify(str(err))
                    self.Notify(message)
                    print(f"LINE:Error occur. Check your Notify")
        
        
        
    def reply_message(self,message,event):
        #リプライのテストを行う場合
        if(str(event) == "test"):
            self.send_message("リプライ挙動チェック：" + "\n" + message,"Notify")
        
        #リプライを返す場合
        else:
            self.line_bot_api.reply_message(event.reply_token,TextSendMessage(message))
            print(f"via API, reply:{message}")



"""
WEBHOOKイベントの中身


{
	"deliveryContext": {"isRedelivery": false},
	"message": {
		"id": "503029853361012850",
		"text": "das", "type": "text"
		},
	"mode": "active",
	"replyToken": "3badb303d2464de78c0b8c65a29a9dbc",
	"source": {
		"groupId": "C6f22ed07319ee447361a16bf9c6c5f33",
		"type": "group", "userId": "U3a6adceb5b40865c2af2b2cfcdc21a2e"
		},
	"timestamp": 1712660461237,
	"type": "message",
	"webhookEventId": "01HV189E3ZTW29Y4SFNZH2P9F4"
}
"""



if __name__ == "__main__" : 
    from data_Roader import roader

    line_bot = LINEBOT(roader())

    line_bot.send_message(message="送信場所変更test",to="C6f22ed07319ee447361a16bf9c6c5f33")
    line_bot.send_message("testtt","Notify")
    line_bot.send_message(message="ノーマルtest")
