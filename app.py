#現在のスクリプトのフォルダを取得してimportに備える
import sys
import os
path = os.path.dirname(__file__);sys.path.append(path)

#変更店を作成する

#pycatchがウザいので生成停止
from sys import dont_write_bytecode;dont_write_bytecode = True



import json
from datetime import datetime


#data.jsonをロードして辞書型を返す魔法
from modules.data_Roader import roader
data = roader()

#LINEを簡単に送れるようになる魔法
from modules.LINE import LINEBOT
line_bot = LINEBOT(data)

#DeepLを使って翻訳をできるようにする魔法
from modules.translate import _DeepL
DeepL = _DeepL(data)

#テストとか用に使う細かいメソッド集
import modules.basement as bas

#logger
logger = bas._logger(path + "/logs/flask.log",True).logger

#flaskをインポート
from flask import Flask, request, abort
#インスタンス作成
static_now = path + "/media"
app = Flask(__name__,static_folder=static_now)
#/media/001.jpgは"https://example.net/media/001.jpg"になる。

#認証ユーザーをロードする
with open(path + "/data/line_users.json","r",encoding="utf-8") as r:
    line_users = json.load(r)


#Hello World!
@app.route("/")
def hello_world():
    return "Hello World!"


#現在のディレクトリを返す
@app.route("/dir")
def back_dir():
    contents = bas.directory_tree(static_now).replace("\n","<br>")

    return contents

#LINE応答用
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_bot.handler.handle(body, signature)
    except line_bot.InvalidSignatureError:
        abort(400)

    
    return 'OK'


@line_bot.handler.add(line_bot.Message_Event, message=line_bot.Text_Message)
def handle_message(event):
    print("res")

    receive = event.message.text
    print("Message:",receive)

    #個別LINE以外のグループなどからメッセージを受け取った場合，toに送り先が指定される。そうでない場合はtoは空
    try:
        to = event.source.group_id
    except:
        to = "None"

    #送信フォーマットを試す。ひとまず半角コロン「:」を指定する
    try:
        mes = receive.split(":.:")
        process = mes[0]
        message = mes[1]

    except:
        process = "None"
        message = receive
    
    print(f"to:{to}")
    
    #メッセージに対する反応
    result = responce(process,message,event,to)
    logger(result)


#メッセージに対する反応
def responce(process , message , event , to = "None"):
    
    sss = str(event)
    user_id = json.loads(sss)["source"]["userId"]
    
    
    #ユーザーIDをもとに検索する
    user = ""
    for key, value in line_users.items():
        #見つけた場合
        if value == user_id:
            
            user = key
            user_id = key
            break
        #見つけられない場合
        else:
            user = "unknown"
   
    
    
    #送信者をlogする
    try:
        short = message[0:4]
    except Exception:
        short = message
    
    logger(f"LINE-from:{str(user_id)} mes:{short}")
    
    
    #未登録ユーザーだった場合
    if user == "unknown":
        line_bot.reply_message("未登録です。使用したい場合は管理者に連絡してください。",event)
        return "NG"
    
    
    #処理指定あり＝プロセスにNone以外
    if(process == "None"):
    #処理指定が何もないメッセージはオウム返し
        line_bot.reply_message(message,event)
        return "OK"
        
    
     #テストテスト
    elif(process == "test" and message == "test" and user == "admin"):
        event_str = str(event)
        line_bot.reply_message("受信テスト完了", event)

        #送信テスト+ローカルipとグローバルipを出力
        ip = bas.ip()

        text = "個別送信テスト完了\nイベント:\n" + event_str + "\n\n\n\n\n" + "Local:" + ip["Local_ip"] + "\n" + "Global:" + ip["Global_ip"]

        line_bot.send_message(text,to)
        return "OK"

     #翻訳する
    elif(process == "翻訳"):
        if(message == "情報"):
            #情報を聞かれた場合は使用履歴を返す
            result = DeepL.usage()

            percent = (1 - result[2]) *100
            count = f"{result[1] - result[0] : ,}"

            text = "{percent}%使用可能(残:{count}字)".format(percent=percent,count=count)

            line_bot.reply_message(text,event)
        else:
            #情報以外の場合は翻訳を返す
            result = DeepL.translate(message)
            line_bot.reply_message(result,event)
        
        return "OK"
    
     #治験データ入力の場合
    elif(process == "治験" and user == "admin"):
        
        now = datetime.now().strftime("%Y-%m-%d")
        
        
        #現在のデータをロードする
        with open(path + "/data/input.json" , "r" , encoding="utf-8") as r:
            input_data = json.load(r)
        
        mes = message.split(":")

        print(mes)
        
        #入力の場合
         #unchi
        if mes[0] == "unchi":
            #info
            if mes[1] == "help":
                text = f'時刻 量  性状(+3=柔、-3=硬) 色(+1=黒、-4=薄) 匂い(+2=強、-2=弱) 残便感(+3=有、0=無) 痛み(0=無、-3=有)\n現在:{input_data["unchi"]}'
                line_bot.reply_message(text,event)
                return "OK"

            #新規入力
            if input_data["unchi"] == "None":
                input_data["unchi"] = mes[1]
                
            #入力済みの場合は改行して追加保存
            else:
                input_data["unchi"] = input_data["unchi"] + "\n" + mes[1]
            
            
            
         #without
        elif mes[0] == "without":
            #info
            if mes[1] == "help":
                text = f'膨満(0=無、+5=強) 腹鳴(0=無、+5=強) ガス(0=無、+5=強)\n現在:{input_data["without"]}'
                line_bot.reply_message(text,event)

            #入力
            input_data["without"] = mes[1]
                
         #life
        elif mes[0] == "life":
            #info
            if mes[1] == "help":
                text = f'酒の種類,量 頻度を変えないやつ,量\n現在:{input_data["life"]}'
                line_bot.reply_message(text,event)
                return "OK"
            
            #入力
            input_data["life"] = mes[1]
                
         #condit
        elif mes[0] == "condit":
            #info
            if mes[1] == "help":
                text = f'体調不良の内容(何時から何時),原因,頻度(0=頻繁,4=ほぼなし) 病院に行った場合は原因\n現在:{input_data["condit"]}'
                line_bot.reply_message(text,event)
                return "OK"
            
            #入力
            input_data["condit"] = mes[1]
        
         #セルフで入力しなおす
        elif mes[0] == "self":
            text = f'https://cpcc.hibilog.jp/mtg24c2/\nID={data["clinical_ID"]}\nPW={data["clinical_ID"]}'     
            line_bot.reply_message(text,event)
            return "OK"

         #リスタートさせる場合
        elif mes[0] == "re":
            try:
                from auto.clinical_trial import main
                line_bot.reply_message("OK",event)
                line_bot.Notify("abc")
            except Exception as err:
                line_bot.reply_message(str(err),event)
            
            return "OK"
            
         #不明な場合，誘導する
        else:
            line_bot.reply_message("unchi,without,life,condit",event)
            return "OK"
        
        #データが更新されたので書き込む
        input_data["date"] = now
        with open(path + "/data/input.json" , "w" , encoding="utf-8") as w:
            json.dump(input_data , w,indent=4,ensure_ascii=False)
        
        
        line_bot.reply_message("入力完了",event)
        
        return "OK"
                    
            
   
    
    
    else:
        line_bot.reply_message("未だない処理", event)
        return "OK"



if __name__ == "__main__" :

    app.run(port=5000)

