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
logger = modules.basement._logger(path + "/logs/marines_announce.log").logger

from modules.LINE import LINEBOT
from modules.data_Roader import roader
line_bot = LINEBOT(roader())

url = 'https://www.marines.co.jp/news/announce/entry'

tmp_name = "logs/marines.tmp"


#xpathのリスト
xpaths ={
    "日付":'//*[@id="content"]/div/div[1]/div/section[3]/div/div/div/div/div/div[1]/div[2]/div/div[2]/div[1]/div[1]',
    "登録":'//*[@id="content"]/div/div[1]/div/section[3]/div/div/div/div/div/div[1]/div[2]/div/div[2]/div[1]/div[2]',
    "抹消":'//*[@id="content"]/div/div[1]/div/section[3]/div/div/div/div/div/div[1]/div[2]/div/div[2]/div[1]/div[3]',

    "年":'//*[@id="content"]/div/div[1]/div/section[3]/div/div/div/div/div/div[1]/div[1]/div[1]/span[1]',
    "月":'//*[@id="content"]/div/div[1]/div/section[3]/div/div/div/div/div/div[1]/div[1]/div[1]/span[2]'

}

#日付を返す
def hiduke(html_txt):
    #日付関係
    date = {
        "年":"",
        "月":"",
        "日":"",
        "曜":""
        }
    
    soup = BeautifulSoup(html_txt, "html.parser")
    lxml_data = html.fromstring(str(soup))

    #年
    date["年"] = lxml_data.xpath(xpaths["年"])[0].text_content()
    #月
    date["月"] = lxml_data.xpath(xpaths["月"])[0].text_content()

    #日付
    result = lxml_data.xpath(xpaths["日付"])
    text_content = result[0].text_content().split()

    #日付の右側1文字(曜日)と数字を分離してリストに格納
    text_content[0] = [text_content[0][:len(text_content[0])-1] , text_content[0][len(text_content[0])-1:]]

    date["日"] = text_content[0][0]
    date["曜"] = text_content[0][1]

    return date

#登録 or 抹消された選手一覧を辞書型で返す
def senshu(html_txt,stat = "登録 or 抹消"):
    Regist = []
    soup = BeautifulSoup(html_txt, "html.parser")
    lxml_data = html.fromstring(str(soup))

    #取得してあるhtmlをxpathをもとに検索，文字列のみ抽出して空白区切りのリストにまとめる
    xpath = xpaths[stat]
    result = lxml_data.xpath(xpath)
    text_content = result[0].text_content().split()

    #リスト空=該当選手なしの場合
    if(len(text_content) == 0):
        return ""

    #数字の数=背番号の場所を取得
    count = []
    for i in range(len(text_content)):
        try:
            int(text_content[i])
            count.append(i)
        except Exception:
            pass
    
    #各選手の情報を取得
    for i in range(len(count)):
        num = count[i]
        person ={
        "ポジション":"",
        "背番号":"",
        "名前":""
        }

        person["ポジション"] = text_content[num-1]
        person["背番号"] = text_content[num]

        #名前を取得する
        if(i != len(count)-1):
            #配列最後以外
            next_num = count[i+1]
            #日本人か助っ人で名前の要素が異なるので区別
            if(num + 4 == next_num):
                #日本人選手の場合
                person["名前"] = text_content[num+1] +" "+ text_content[num+2]

            else:
                #助っ人の場合
                person["名前"] = text_content[num+1]

        else:
            #配列最後

            #日本人か助っ人で名前の要素が異なるので区別
            if(num + 2 == len(text_content) - 1):
                #日本人選手の場合
                person["名前"] = text_content[num+1] +" "+ text_content[num+2]
            else:
                #助っ人の場合
                person["名前"] = text_content[num+1]

        #リストに追加
        Regist.append(person)
        
    return Regist

#LINEに送信するための文面を作る
def sender(base,Play):

    if(Play != ""):
        result = base

        for elem in Play:
            result = result + '\n' + "{name}({number})".format(name=elem["名前"],number=elem["背番号"])
    else:
        result = base +"\n"+"該当者なし"

    return result

#新しく取得した情報をもとにLINEに送信する
def newer(html_txt , to = ""):
    #日付
    date = hiduke(html_txt)
    #登録
    Regist = senshu(html_txt,"登録")
    #抹消
    DeRegist = senshu(html_txt,"抹消")

    #現在の月日と取得した月日を比較する
    now = int(datetime.datetime.now().strftime('%m') +datetime.datetime.now().strftime('%d'))
    date_int = int(date["月"] + date["日"])
    if now != date_int:
        return False


    #LINEに送信
    date = "マリーンズの{YY}年{MM}月{DD}日({aaa})の公示をお伝えします。".format(YY=date["年"], MM=date["月"], DD=date["日"], aaa=date["曜"])
    

    Regi = sender("登録：",Regist)

    DeRegi = sender("抹消：",DeRegist)

    Mass_str = date + "\n" + Regi + "\n" + DeRegi

    line_bot.send_message(Mass_str,to)

    #確認できたファイルを出力する
    soup = BeautifulSoup(html_txt, "html.parser")
    lxml_data = html.fromstring(str(soup))
    kakunin = lxml_data.xpath('//*[@id="content"]/div/div[1]/div/section[3]/div/div/div/div/div/div[1]')[0].text_content()

    with open(path +"/"+ tmp_name , "w",encoding='utf-8') as f:
    #上書きする
        f.write(kakunin)
    
    return True

#更新されているかどうか確認してから送る
def reload1234(url,base,to = ""):
    print("カク")
    html_txt = requests.get(url).text

    soup = BeautifulSoup(html_txt, "html.parser")
    lxml_data = html.fromstring(str(soup))
    ima = lxml_data.xpath('//*[@id="content"]/div/div[1]/div/section[3]/div/div/div/div/div/div[1]')[0].text_content()

    if(base != ima):
        return newer(html_txt , to)
    
    return False


if __name__ == "__main__":
    from time import sleep as wait
    import datetime

    #現在作成されている更新リストを開く
    try:
        with open(path +"/"+ tmp_name,"r",encoding='utf-8') as r:
            base = r.read()
    except Exception:
        with open(path +"/"+ tmp_name,"w",encoding='utf-8') as r:
            base = r.write("")

    start = datetime.datetime.now()
    #更新されるまで待つ
    while  True:
        #送信先
        to = "Notify"

        delta = datetime.datetime.now() - start

        limit = datetime.timedelta(hours=6)


        #経過時間がリミットより小さい場合は更新確認，大きい場合はメッセージを送って終了
        if(delta < limit):
            
            #更新チェック
            result = reload1234(url,base,to)
            logger("check")
            if(result):
                logger("公示確認。終了")
                break

            wait(600)
        if(limit < delta):
            idx = datetime.datetime.now().strftime('%u')  # '%u'では月曜日がインデックス'1'となる
            w = '日月火水木金土日'[int(idx)]

            d = datetime.datetime.now().strftime('%Y年%m月%d日') + f'({w})'

            #line_bot.send_message(f"マリーンズの{d}の公示はありませんでした。",to)
            logger("公示なし。中断")
            break


        
    


    
    


