version = "1.0.0"
from sys import dont_write_bytecode;dont_write_bytecode = True
from os.path import dirname;path = dirname(dirname(dirname(__file__)))
import sys; sys.path.append(path)


import requests
import json
from datetime import datetime , timedelta

#参考url
"https://dev.fitbit.com/build/reference/web-api/troubleshooting-guide/oauth2-tutorial/"
"https://dev.fitbit.com/apps/"


base = "https://api.fitbit.com/"

#オフセットを設定する。1日前とかにもできる
offset = -timedelta(days=0)

#リフレッシュトークンによるアクセストークン更新
def refresh(user_data):
    
    
    Ref_Token = user_data["fitbit_Ref_Token"]
    Client_id = user_data["fitbit_Client_id"]
    
    #権限エラーでref_Tokenが書き込めないと本当に面倒くさいことになるので最初にアクセストークンを消去しとく
    user_data["fitbit_Acc_Token"] = ""
    with open(path + "/data/secret.json","w",encoding="utf-8") as w:
        json.dump(user_data,w,indent=4)
    
    
    #更新用送信データ作成
    data={
        
        "grant_type": "refresh_token",
        "refresh_token": f"{Ref_Token}",
        "client_id": Client_id
    }


    url = "https://api.fitbit.com/oauth2/token"

    #更新のリクエストを行う
    result = requests.post(url,data=data).json()

    #手持ちのtokenは空になっているので取得したアクセストークンを書き込む
    user_data["fitbit_Acc_Token"] = result["access_token"]
        
    #リフレッシュトークンは一回限りなので更新する
    user_data["fitbit_Ref_Token"] = result["refresh_token"]
    
    #書き込み
    with open(path + "/data/secret.json","w",encoding="utf-8") as w:
        json.dump(user_data,w,indent=4)
        
    return user_data



#fitbitAPIを用いて生睡眠データを取得する
def fitbit_API_sleep(user_data):
       
    Acc_Token = user_data["fitbit_Acc_Token"]
    #送信用queryを作成する
    def query_parameters():
        
       
        now = datetime.now() + timedelta(days=1) + offset

        today = now.strftime("%Y-%m-%d") 
        
        que = {
            "beforeDate":today,
            "afterDate":"",
            "sort":"desc",
            "limit":7,
            "offset":0       
        }
        
        result = ""
        for elem in que:
            
            if que[elem] != "":
                result += f"{elem}={que[elem]}&"
        
        return result[:-1]

    
    #開始----------------------
    

    #queryを含むurlを作成する
    url = base + "/1.2/user/-/sleep/list.json" + "?" + query_parameters()

    result = requests.get(url,headers={"Authorization": f"Bearer {Acc_Token}"}).json()

    
    
    
    #結果をファイルに書き込んでおく
    with open(path + "/logs/sleep.json","w",encoding="utf-8") as w:
        json.dump(result , w , indent=4)
        
    return result


#生の睡眠データを良い形に変換する
def sleep_adjust(raw_data={}):
    
    if raw_data == {}:
        #データの入力がない場合はロードする
        with open(path + "/logs/sleep.json" , "r" , encoding="utf-8") as r:
            raw_data = json.load(r)
        
    
    #データ整理
    midiate1 = raw_data["sleep"]
    last = []
    
    #日付と時間だけを出力
    for i in range(len(midiate1)):
               
        #同じ日であった場合は合計する
        if i != 0 and midiate1[i]["dateOfSleep"] == midiate1[i-1]["dateOfSleep"]:
            last[i-1]["time"] = last[i-1]["time"] + midiate1[i]["duration"]
        
        #初めての日のデータの場合
        else:
            date = midiate1[i]["dateOfSleep"]
            time = midiate1[i]["duration"]
            
            last.append(
                {
                    "date":date,
                    "time":time
                    
                }
                
                
            )
            
        

    #時間をmsからhに変える
    for i in range(len(last)):
        
        #ms->h
        midi = last[i]["time"] /10**3 /  60**2
        
        #丸める
        midi = round( midi,1)
        
        #0.5刻みじゃない場合
        if midi % 0.5 != 0 or midi < 1:
            other = midi % 0.5
            
            
            base = midi - other
            
            #あまりが 0~0.25
            if 0.00 < other <= 0.25:
                midi = base + 0
            #あまりが 0.25~0.50
            if 0.25 < other <= 0.50:
                midi = base + 0.5
            #あまりが 0.50~0.75
            if 0.50 < other <= 0.75:
                midi = base + 0.5
            #あまりが 0.75~0.999
            if 0.75 < other < 1:
                midi = base + 1
                

        last[i]["time"] = midi

    
    return last


#睡眠データを取得する
def sleep_data(user_data):

    user_data = refresh(user_data)

    raw_data = fitbit_API_sleep(user_data)

    result = sleep_adjust(raw_data)
    
    now = datetime.now() + offset

    today = now.strftime("%Y-%m-%d")
    
    
    
    #今日の分の睡眠時間を取得する
    for elem in result:
        if elem["date"] == today:
            return elem["time"]

#APIを利用して今日の歩数を出力する
def fitbit_API_steps(user_data):
    
    Acc_Token = user_data["fitbit_Acc_Token"]
    
    
    now = datetime.now() + offset
    today = now.strftime("%Y-%m-%d")
    
    url = base + f"/1/user/-/activities/date/{today}.json"
    
    result = requests.get(url,headers={"Authorization": f"Bearer {Acc_Token}"}).json()
    
    #result = json.dumps(result,indent=4)
    
    steps = result["summary"]["steps"]
    
    return steps

#歩数データを取得する
def step_data(user_data):
    
    user_data = refresh(user_data)
    
    steps = fitbit_API_steps(user_data)
    
    return steps

#インポート用
def main(user_data):
        
    sle = sleep_data(user_data)
    
    ste = step_data(user_data)
    
    last={
        "sleep":sle,
        "steps":ste        
    }
    
    
    return last
    
    


if __name__ == "__main__":
    
    #データ読み込み
    with open(path + "/data/secret.json" , "r" , encoding="utf-8") as r:
        user_data = json.load(r)
    
    
    result = main(user_data)
    
    
    print(f'sleep={result["sleep"]},steps={result["steps"]}')











































