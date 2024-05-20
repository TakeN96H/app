#htmlを取得
import requests
from bs4 import BeautifulSoup
from lxml import html

#親ファイルをパスに入れる
import os , sys
path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(path)
#pycatchがウザいので生成停止
from sys import dont_write_bytecode;dont_write_bytecode = True


import modules.basement
logger = modules.basement._logger(path + "/logs/marines_starting.log").logger

from modules.LINE import LINEBOT
from modules.data_Roader import roader
line_bot = LINEBOT(roader())

import datetime
from time import sleep as wait

team = "ロッテ"

#{/@href}でクリック時のリンクを取得することができる
xpaths={
    "game":'//*[@id="gm_card"]/section[2]/ul/li[{0}]',
    "link":'//*[@id="gm_card"]/section[2]/ul/li[{0}]/a',
    "order":'//*[@id="strt_mem"]/section/div/section[{0}]',
    "jadge":'//*[@id="benc_mem"]/div',
    "bench":'//*[@id="benc_mem"]/section[{typer}]/div/section[{team}]',
    "pacific":'//*[@id="gm_card"]/section[2]/header/h1'

}

class MyException(Exception):
    pass

#試合表のうちロッテが含まれる場所を取得してxpathのliの番号を出力する
def game_list(lxml_data):
    
    num = 99
    
    #パリーグを検知する
    try:
        data = lxml_data.xpath(xpaths["pacific"])[0].text_content()
        if data.find("パ・リーグ") == -1 :
            return "NG1"
    except Exception:
        return "NG2"


    for i in range(5):
        data = lxml_data.xpath(xpaths["game"].format(i))
        #
        if(len(data) != 0):

            abc = str(data[0].text_content())
        else:
            abc = ""

        lotty = abc.find(team)

        #ロッテが見つかった場合は番号を返す
        if(lotty != -1):
            num = i


    return num

#ロッテがあるxpath番号を入れリンクを取得
def get_link(lxml_data , num):

    #xpathからリンクを取得する
    data = lxml_data.xpath((xpaths["link"] + '/@href').format(num))[0]

    return data

#スタメンを出力する
def starting_menber(lxml_data):

    num = 99
    #ロッテがどっちかわからないので探す
    for i in range(1,3):
        data = lxml_data.xpath(xpaths["order"].format(i))[0].text_content()

        if(data.find(team) != -1):
            num = i

    #見つからなかったら
    if num == 99:
        raise MyException("cant find starting lineup")

    data = lxml_data.xpath(xpaths["order"].format(num))[0].text_content().split()
    
    #整形する
    order = []

    num_list = []
    for i in range(len(data)):
        try:
            int(data[i])
            num_list.append(i)
        except Exception :{}
    num_list.append(len(data))
    #ピッチャーを抽出
    pitcher = data[8]


    #1番から9番まで抽出
    for i in range(9) :
        person={
            "打順":i+1,
            "ポジション":"",
            "名前":"",
            "バッターボックス":"",
            "打率":""

        }

        delta = num_list[i+1] - num_list[i]

        person["ポジション"] = data[num_list[i] + 1]
        person["名前"] = data[num_list[i] + 2]
        person["バッターボックス"] = data[num_list[i] + delta - 2]
        person["打率"] = data[num_list[i] + delta - 1]

        

        order.append(person)


    return pitcher , order , num

#リストを検索して防御率 or 打率から名前を出力する
def sercher(ex_list):

    #防御率 or 打率を消去する
    del ex_list[0]
    del ex_list[1]

    #ピッチャーの名前を抽出
    num_pit =[0]
    for i in range(len(ex_list)):
        try:
            #防御率を抽出(登板なしの場合"-"なのでそれにも対応)
            if(ex_list[i] != "-"):
                float(ex_list[i])
            num_pit.append(i)
        except Exception :{}


    result_list =[]
    for i in range(1,len(num_pit)):

        #ひとつ前が4コ前=名前2列の場合
        if(num_pit[i-1] == num_pit[i] - 4):
            select = num_pit[i] - 3
            result_list.append(ex_list[select])
        #ひとつ前が3コ前=名前1列の場合
        if(num_pit[i-1] == num_pit[i] - 3):
            select = num_pit[i] - 2
            result_list.append(ex_list[select])
        
    return result_list

#ベンチ入りの選手を出力する
def bencher(lxml_data , num):
    #探す

    for i in range(1,5):
        
        data = lxml_data.xpath(xpaths["bench"].format(typer=i,team=num))[0].text_content().split()

        if(i == 1):
            pitchers = sercher(data)
        if(i == 2):
            catchers = sercher(data)
        if(i == 3):
            infielders = sercher(data)
        if(i == 4):
            outfielders = sercher(data)


    result={
        "pitchers":pitchers,
        "catchers":catchers,
        "infielders":infielders,
        "outfielders":outfielders
    }

    return result

#送信用文面を作成する
def rebuilder(pitcher , batters , benches):
    result = f"先発：\n投手 {pitcher}\n"

    for elem in batters:
        result += f'{elem["打順"]} ({elem["ポジション"]}) {elem["名前"]}\n'

    result += "\n投手ベンチ:\n"
    for elem in benches["pitchers"]:
        result += elem + " "

    result += "\n捕手ベンチ:\n"
    for elem in benches["catchers"]:
        result += elem + " "

    result += "\n内野ベンチ:\n"
    for elem in benches["infielders"]:
        result += elem + " "
    result += "\n外野ベンチ:\n"
    for elem in benches["outfielders"]:
        result += elem + " "
    
    return result

#日付とゲーム時間を取得する
def game_time(lxml_data , num):
    #xpathから日付と試合状況を取得する
    data = lxml_data.xpath(xpaths["link"].format(num))[0].text_content().split()
    

    return data

#元urlから条件分岐して試合urlを返す
def requirement (url , testmode = False) :

    if testmode == True:
        html_data = url
    else:
        html_data = requests.get(url).text

    soup = BeautifulSoup(html_data, "html.parser")
    lxml_data = html.fromstring(str(soup))

    #本日のゲーム一覧からロッテの試合を取得する。試合がない場合はエラー分岐
    num = game_list(lxml_data)
    if type(num) == str :
        raise MyException("cant find pacific league")

    #各種ゲーム情報を取得
    gamedata = game_time(lxml_data,num)

    #取得した月日をintの4文字以内で出力し，今日の日付と照合，間違っている場合はエラー分岐
    now = int(datetime.datetime.now().strftime('%m') +datetime.datetime.now().strftime('%d'))
    game_date = gamedata[0]
    date = ""
    for elem in game_date :
        try:
            int(elem)
            date += str(elem)
        except Exception : {}
    gamedate = int(date)
    if(gamedate != now):
        raise MyException("date difference")

    #ゲーム状況確認
    game_statu = gamedata[5]
    #ステータス確認し，不備があればエラー
    if(game_statu == "スタメン"):
        pass
    elif(game_statu == "見どころ"):
        raise MyException("not opened")
    elif(game_statu == "試合終了"):
        raise MyException("ended")
    elif(game_statu == "試合中止"):
        raise MyException("canceled")
    else:
        raise MyException("unknown")
    
    
    #本日の試合のurlを取得する
    game_url = get_link(lxml_data,num)
    return game_url

#スタメンとベンチをまとめてLINEに送信する
def sender(game_url, testmode = False):
    try:
        
        #試合の情報を取得する(testの場合はurlにhtmlを入れておく)
        if(testmode == False):
            html_data = requests.get(game_url).text
        else:
            html_data = game_url

        soup = BeautifulSoup(html_data, "html.parser")
        lxml_data = html.fromstring(str(soup))

        #先発，スタメン，ベンチを取得する
        pitcher , batters , num = starting_menber(lxml_data)
        benches = bencher(lxml_data,num)

        message = rebuilder(pitcher,batters,benches)

        line_bot.send_message(message,"Notify")

        #送信完了
        
        return "OK"
    
    except Exception as err:
        #エラー発生
        return f"NG,{str(err)}\n"

#スタメン発表されるまで待つ
def looper(url , tester = False):
    count = 0
    while True:
        try:
            result = requirement(url,tester)
            return result
        except MyException as err:
            err = str(err)
            if(err == "not opened"):
                pass
            else:
                return err
        wait(300)
        
        #6時間割る5分で72
        if(72 < count):
            return "for 6 hours"
        count += 1


if __name__ == "__main__":

    logger("start")

    url = looper("https://baseball.yahoo.co.jp/npb/")

    if(url[0:5] != "https"):
        logger(f"NG, {str(url)}")
        raise MyException(url)

    result = sender(url)

    logger("succese")






