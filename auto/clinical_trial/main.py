version = "1.0.0"
from sys import dont_write_bytecode;dont_write_bytecode = True
from os.path import dirname;path = dirname(dirname(dirname(__file__)))
import sys; sys.path.append(path)

#自作モジュール
from modules.basement import _logger
from modules.data_Roader import roader as _roader
from auto.clinical_trial.inputer import main as inputer
from auto.clinical_trial.fitbit import main as fitbit
from modules.LINE import LINEBOT

#自作インスタンス
user_data = _roader()
logger = _logger(path + "/logs/clinical_input.log").logger
notify = LINEBOT(user_data).Notify


import json

from datetime import datetime , timedelta


    
default ={
    "date":"",
    "unchi":"None",
    "without":"n n n",
    "life":"None みそ汁,1杯300ml",
    "condit":"None None"
}



now = datetime.now()

today = str(now.strftime('%Y') +"-"+ now.strftime('%m') +"-"+ now.strftime('%d')) 

#連携データを読み込む
with open(path + "/data/input.json","r",encoding="utf-8") as r:
    data = json.load(r)

#データをロードする
date = data["date"]
unchi = data["unchi"]
without = data["without"]    

#fitbitを入力するのでこっちで入力できるものは酒の種類と頻度を変えないやつのみ
life = data["life"]

#lifeを整形
midiate1 = life.split(" ")

fitb = fitbit(user_data)

life = f'{midiate1[0]} {fitb["steps"]} {fitb["sleep"]} {midiate1[1]}'

condit = data["condit"]

#データの入力がされていない場合
if date != today:
    
    notify(f"[{today}]治験データ 入力されていません")
    logger("データ入力なし")
    
    quit()

#メイン入力
try:
    print(unchi)
    inputer(user_data , unchi,without,life,condit)
    
    #流れてきた=成功
    notify(f"[{today}]治験データ 完了")
    logger("入力完了")
    
    #入力し終わったのでデータをデフォルトに戻す
    with open(path + "/data/input.json","w",encoding="utf-8") as w:
        json.dump(default,w,indent=4)
    
    
except Exception as err:
    #失敗
    notify(f"[{today}]治験データ 失敗\n{err}")
    
    logger(err)
