version = "1.0.0"
from sys import dont_write_bytecode;dont_write_bytecode = True
from os.path import dirname;path = dirname(dirname(dirname(__file__)))
import sys; sys.path.append(path)


from datetime import datetime , timedelta

from modules.seleniumed import selen


URL_base = "https://cpcc.hibilog.jp/mtg24c2/"
URL_daily = URL_base + "epro/daily/"

class Myerr(Exception):{}

#xpath一覧
xpaths={
    #ログイン
    "ID": '//*[@id="username"]',
    "PW": '//*[@id="password"]',
    "LG": '//*[@id="main"]/div[5]/button',

    #日付選択
    "Table": R'//*[@id="nav-calendar"]/div/div[2]/div/table/tbody/tr[{}]', #テーブル、Dates=日付(日曜から土曜)、1~7
    "Date": R'/td[{}]/div/button', #Date=その日の状況、1=日付、2=入力状況、tableの続き

    #うんちはじめ
    "poopss": {

        #はい・いいえ
        "tf": '//*[@id="q_id_7087_{}"]',#12103~12104=無

        #テーブル一覧
        "in": '//*[@id="7088_row_index_{}"]',#0からスタート、追加ボタンを押すと増えていく

        #追加ボタン
        "bt": '//*[@id="q_id_7088_add_button"]',#追加ボタン、クリック

        #回数
        "ti": '//*[@id="q_id_7105"]',#回数

        #n回目----
        "single":{

            #排便時刻
            "time_hh": '//*[@id="q_id_7091_{index}"]',#キーボード
            "time_mm": '//*[@id="q_id_7092_{index}"]',

            #採便しましたか
            "coll_tf": '//*[@id="q_id_7094_{index}_{}"]',#12105=はい、12106=いいえ

            #量
            "amou_ky": '//*[@id="q_id_7098_{index}"]',#キーボード

            #性状
            "char_mt": '//*[@id="q_id_7099_{index}_{}"]', #12151~12157

            #色
            "colo_mt": '//*[@id="q_id_7100_{index}_{}"]', #12158~12163

            #匂い
            "smel_mt": '//*[@id="q_id_7101_{index}_{}"]', #12164~12168

            #排便時の残便感
            "left_mt": '//*[@id="q_id_7102_{index}_{}"]', #12169~12172

            #排便時の腹部の痛み
            "pain_mt": '//*[@id="q_id_7103_{index}_{}"]',#12173~12176


        },
    },
        #排便時以外の時間帯におけるお腹の状態----
    "wthout": {

        #膨満感
        "full_mt": '//*[@id="q_id_7109_{}"]',#12187~12192

        #腹鳴
        "grug_mt": '//*[@id="q_id_7111_{}"]',#12193~12198

        #ガス
        "gass_mt": '//*[@id="q_id_7113_{}"]',#12199~12204
    },

    #研究食品の摂取について----
    "reserc": {

        #研究食品を摂取しましたか
        "incu_tf": '//*[@id="q_id_7176_12276"]',#はい固定

        #接種数
        "amoun_tt": '//*[@id="q_id_7178_12283"]',#2袋固定にしておく



    },

    #生活について----
    "tdayli":{

        #1日を通しての食事回数・りょうについて
        "meal_tt": '//*[@id="q_id_7116_12205"]',#普段通り固定

        #お酒を飲みましたか
        "drun_li":{
            #はい・いいえ
            "tf": '//*[@id="q_id_7120_{}"]',#12207~12208

            #お酒の種類
            "na": '//*[@id="q_id_7122"]',#キーボード

            #お酒の量
            "am": '//*[@id="q_id_7123"]'#キーボード

        },

        #運動しましたか
        "exer_tf": '//*[@id="q_id_7125_12210"]',#いいえ固定

        #1日の歩数
        "step_ky": '//*[@id="q_id_7130"]',#キーボード

        #睡眠時間
        "slee_ky": '//*[@id="q_id_7133"]',#キーボード、0.5ずつ

        #生活の変化はありましたか
        "chen_tf": '//*[@id="q_id_7135_12254"]',#いいえ固定

        #特保などを摂取しましたか
        "toku_tf": '//*[@id="q_id_7138_12256"]',#いいえ固定

        #摂取をしないやつを摂取しましたか
        "tabo_tf": '//*[@id="q_id_7143_12258"]',#いいえ固定

        #頻度を変えないでほしいやつを摂取しましたか
        "freq_li":{
            #はい・いいえ
            "tf": '//*[@id="q_id_7148_{}"]',#12259~12260

            #製品名
            "na": '//*[@id="q_id_7150"]',#キーボード

            #摂取量
            "am": '//*[@id="q_id_7151"]',#キーボード


        }


    },

    #体調について----
    "condit":{

        #体調不良はありましたか
        "cond_li":{

            #はい・いいえ
            "tf": '//*[@id="q_id_7154_{}"]',#12261~12262

            #症状・時間
            "st": '//*[@id="q_id_7156"]',#キーボード

            #原因
            "re": '//*[@id="q_id_7157"]',#キーボード

            #頻度
            "fr": '//*[@id="q_id_7158_{}"]',#12263~12266


        },

        #病院を受診しましたか
        "hosp_li":{

            #はい・いいえ
            "tf": '//*[@id="q_id_7161_{}"]',#12267~12268

            #原因
            "re": '//*[@id="q_id_7163"]',#キーボード

        },

        #本日ワクチンを接種しましたか
        "vacc_tf": '//*[@id="q_id_7165_12270"]',#いいえ固定

        #医療品を使用しましたか
        "medi_tf": '//*[@id="q_id_7170_12275"]',#いいえ固定



    },

    #保存して進む
    "savean": '//*[@id="main"]/article/div/div[2]/div[1]/div/button[2]'

}


#ページにある分を参照してxpathを全部取る
def verify(Input_Status):
    now = datetime.now()


    today = str(now.strftime('%Y') +"/"+ now.strftime('%m') +"/"+ now.strftime('%d'))

    #各配列の0番と今日の日付を比較する
    Previous = True
    today_num = 99

    for i in range(len(Input_Status)):

        elem = Input_Status[i]

        #当日分
        if elem[0] == today:
            Previous = False
            #未入力であることを確認
            if elem[3] == "未入力" or elem[3] == "入力中":
                #取得したテーブルの様式に合わせて今日の場所を入力
                today_num = i + 1

                #当日のxpath
                return xpaths["Table"].format(today_num) + xpaths["Date"].format("2")


            elif elem[3] == "入力済" or elem[3] == "〇":
                raise Myerr("今日の分は既に入力済です")

            else:
                raise Myerr("不正なステータス")

        #前分、Previous=Trueの時に参照
        elif Previous:
            #前分の入力ステータスを検証
            if elem[2] == "未入力":

                raise Myerr("前日分までが入力されていません")

#---------------------------------------

#うんち入力文字列を通常に変換する
def organize_unchi(data :str):

    #スペースで個別の情報、改行で回数
    first = data.split("\n")

    #1回ごとのデータに分ける
    midiate = []
    for elem in first:
        elem = elem.split(" ")

        midiate.append(elem)
        
        #入力しない場合
        if elem[0] == "None":
            return "None"
        
        
        #時刻と量が足りない場合
        if len(elem) < 2 :
            raise Myerr("入力形式が間違っています。時間と量を入力してください")
        


    #時刻を補正
    for i in range(len(midiate)):
        after = [ midiate[i][0][0:2] , midiate[i][0][2:4] ]

        midiate[i][0] = after


    #辞書型に代入して最終データ
    last = []
    for elem in midiate:

        for i in range(6 - len(elem) + 1):
            elem.append("n")

        #量は0.5刻みなのでそれ以外だったら切り捨てる
        elem[1] = float(elem[1]) if( float(elem[1]) % 0.5 != 0 )else float(elem[1]) - float(elem[1]) % 0.5
        
        #テンプレに代入してappendしようとすると全部同じデータになってまう。メモリ参照のミスなので修正は厳しいかも
        last.append(
            {
            #何回目
            "num": 0,

            #各データ
            "single":{

                #排便時刻
                "time_hh": int(elem[0][0]),
                "time_mm": int(elem[0][1]),

                #採便しましたか
                "coll_tf": 'False',#True or False

                #量
                "amou_ky": elem[1],#卵の数、0.5刻み

                #性状
                "char_mt": 4-1 if elem[2] == "n" else int(elem[2]) + 4 -1,#1~7

                #色
                "colo_mt": 5-1 if elem[3] == "n" else int(elem[3]) + 5 -1,#1~6

                #匂い
                "smel_mt": 3-1 if elem[4] == "n" else int(elem[4]) + 3 -1,#1~5

                #排便時の残便感
                "left_mt": 1-1 if elem[5] == "n" else int(elem[5]) + 1 -1,#1~4

                #排便時の腹部の痛み
                "pain_mt": 4-1 if elem[6] == "n" else 4 - int(elem[6]) -1,#1~4

            }})

    return last

#ループありの個別入力
def loop_inputer(sc,unchies):
    #排便の有無
    if unchies == "None":#なし
        xpath = xpaths["poopss"]["tf"].format("12104")
        sc.find(xpath).click()
        return "OK"

    else:#あり
        xpath = xpaths["poopss"]["tf"].format("12103")
        sc.find(xpath).click()
    
    
    #ループ
    for i in range(len(unchies)):

        data = unchies[0]["single"]


        base= xpaths["poopss"]["single"]
        
        #排便時間
        xpath1 , xpath2 = base["time_hh"].format(index=i) , base["time_mm"].format(index=i)
        sc.find(xpath1).send(data["time_hh"])
        sc.find(xpath2).send(data["time_mm"])
        
        #採便しましたか
        xpath = base["coll_tf"].format("12106" , index=i)
        sc.find(xpath).click()
        
        #量
        xpath = base["amou_ky"].format(index=i)
        sc.find(xpath).send(data["amou_ky"])

        #性状
        xpath = base["char_mt"].format(12151 + data["char_mt"], index=i)
        sc.find(xpath).click()
        
        #色
        xpath = base["colo_mt"].format(12158 + data["colo_mt"], index=i)
        sc.find(xpath).click()
        
        #匂い
        xpath = base["smel_mt"].format(12164 + data["smel_mt"], index=i)
        sc.find(xpath).click()
        
        #残便感
        xpath = base["left_mt"].format(12169 + data["left_mt"], index=i)
        sc.find(xpath).click()
        
        #腹部痛み
        xpath = base["pain_mt"].format(12173 + data["pain_mt"], index=i)
        sc.find(xpath).click()
        
        #入力した分を消す
        del unchies[0]
        
        #追加する場合→追加ボタンクリック
        if len(unchies) != 0:
            xpath = xpaths["poopss"]["bt"]
            sc.find(xpath).click()
        
        #最後の処理→回数入力
        if len(unchies) == 0:
            xpath = xpaths["poopss"]["ti"]
            sc.find(xpath).send(i + 1)

#---------------------------------------

#お腹の状態文字列を通常に変換する
def organize_with(data :str):
    
    #区切り
    data = data.split()
   
    if len(data) < 3:
       data.append("n")
    last = {
        "full_mt": 0 if data[0] == "n" else int(data[0]),
        "grug_mt": 0 if data[1] == "n" else int(data[1]),
        "gass_mt": 0 if data[2] == "n" else int(data[2])
        
        
    }
    
    return last

#排便以外のおなかの状況
def with_inputer(sc,withouts):
    base = xpaths["wthout"]
    
    #膨満感
    xpath = base["full_mt"].format(12187 + withouts["full_mt"])
    sc.find(xpath).click()
    
    #腹鳴
    xpath = base["grug_mt"].format(12193 + withouts["grug_mt"])
    sc.find(xpath).click()
    
    #ガス
    xpath = base["gass_mt"].format(12199 + withouts["gass_mt"])
    sc.find(xpath).click()

#---------------------------------------

#生活の状態文字列を通常に変換する
def organize_life(data :str):
    
    #スペースで区切る
    midiate1 = data.split()
    
    #個別のカンマで区切る
    midiate2 = []
    for elem in midiate1:
        midiate2.append(elem.split(","))
    
    #酒と頻繁にとるやつの行列の有効性を確認
    if len(midiate2[0]) != 2:
        midiate2[0].clear()
        
        midiate2[0].append("None")
        midiate2[0].append("")
        
    if len(midiate2[3]) != 2:
        midiate2[3].clear()
            
        midiate2[3].append("None")
        midiate2[3].append("")
    
    #睡眠時間は0.5刻みなのであまりを切り捨てる
    midiate2[2][0] = float(midiate2[2][0]) if( float(midiate2[2][0])%0.5 != 0 )else  float(midiate2[2][0]) - float(midiate2[2][0]) % 0.5
        

    last = {
        "drun_li":{
           "na": midiate2[0][0],
           "am": midiate2[0][1]
        },
    
       "step_ky": midiate2[1][0],#できれば自動でとってきたい
       "slee_ky": midiate2[2][0],#できれば自動でとってきたい
    
       "freq_li":{
           "na": midiate2[3][0],
           "am": midiate2[3][1]
       }
    }

    return last

#生活習慣の入力
def life_inputer(sc,lifes):
    base = xpaths["tdayli"]
    
    #1日を通しての食事、普段通り固定
    xpath = base["meal_tt"]
    sc.find(xpath).click()
    
    
    #お酒を飲んだか
    if lifes["drun_li"]["na"] == "None":#飲んでない
        #いいえにチェック
        xpath = base["drun_li"]["tf"].format(12208)
        sc.find(xpath).click()#
        
    else:#飲んだ
        
        #はいにチェック
        xpath = base["drun_li"]["tf"].format(12207)
        sc.find(xpath).click()
        
        #種類を入力
        xpath = base["drun_li"]["na"]
        sc.find(xpath).send(lifes["drun_li"]["na"])
        
        #量を入力
        xpath = base["drun_li"]["am"]
        sc.find(xpath).send(lifes["drun_li"]["am"])
    
    
    #運動をしたか、いいえ固定
    xpath = base["exer_tf"]
    sc.find(xpath).click()
    
    
    #歩数
    xpath = base["step_ky"]
    sc.find(xpath).send(lifes["step_ky"])
    
    #睡眠時間
    xpath = base["slee_ky"]
    sc.find(xpath).send(lifes["slee_ky"])
    
    #生活に変化あったか、特保等とったか、禁止を食べたか、全部いいえ固定
    xpath1 , xpath2 , xpath3 = base["chen_tf"] , base["toku_tf"] , base["tabo_tf"]
    sc.find(xpath1).click()
    sc.find(xpath2).click()
    sc.find(xpath3).click()
    
    #頻度を変えないでほしいものをとったか
    if lifes["freq_li"]["na"] == "None":#取ってない
        xpath = base["freq_li"]["tf"].format(12260)
        sc.find(xpath).click()
    else:#取った
        xpath = base["freq_li"]["tf"].format(12259)
        sc.find(xpath).click()
        
        #製品名を入力
        xpath = base["freq_li"]["na"]
        sc.find(xpath).send(lifes["freq_li"]["na"])
        
        #量を入力
        xpath = base["freq_li"]["am"]
        sc.find(xpath).send(lifes["freq_li"]["am"])

#---------------------------------------

#体調の状態文字列を通常に変換する
def organize_cond(data :str):
    #スペースで区切る
    midiate1 = data.split()
    
    #個別のカンマで区切る
    midiate2 = []
    for elem in midiate1:
        midiate2.append(elem.split(","))
    
    
    #体調不良の有効性を確認
    if len(midiate2[0]) != 3:
        midiate2[0].clear()
       
        midiate2[0].append("None")
        midiate2[0].append("")
        midiate2[0].append("")

    #最終調整
    last ={
        #体調不良はありましたか
        "cond_li":{  
            "st": midiate2[0][0],
            "re": midiate2[0][1],
            "fr": midiate2[0][2],#頻度、0~2で指定、下に行くほど頻度が下がる。最後はその他なのでやらないこと
        },
        
        #病院を受診しましたか
        "hosp_li":{
           "re": midiate2[1][0],
           
        }
    }
    
    return last

#体調について
def cond_inputer(sc,condits):
    base = xpaths["condit"]
    
    #体調不良
    if condits["cond_li"]["st"] == "None":#なにもない
        xpath = base["cond_li"]["tf"].format(12262)
        sc.find(xpath).click()
    else:#なんかあった
        xpath = base["cond_li"]["tf"].format(12261)
        sc.find(xpath).click()            
        
        #症状・時間
        xpath = base["cond_li"]["st"]
        sc.find(xpath).send(condits["cond_li"]["st"])
        
        #原因
        xpath = base["cond_li"]["re"]
        sc.find(xpath).send(condits["cond_li"]["re"])
        
        #頻度
        xpath = base["cond_li"]["fr"].format(12263 + int(condits["cond_li"]["fr"]))
        sc.find(xpath).click()
    
    #病院
    if condits["hosp_li"]["re"] == "None":#何もない
        xpath = base["hosp_li"]["tf"].format(12268)
        sc.find(xpath).click()
    else:#いった
        xpath = base["hosp_li"]["tf"].format(12267)
        sc.find(xpath).click()
        
        #原因
        xpath = base["hosp_li"]["re"]
        sc.find(xpath).send(condits["hosp_li"]["re"])
    
    #ワクチンを接種しましたか
    xpath = base["vacc_tf"]
    sc.find(xpath).click()
    
    #医療品を使用しましたか
    xpath = base["medi_tf"]
    sc.find(xpath).click()



#メイン、インポートして入力する予定なのでそれ用
def main(user_data , unchi , without , life , condit):
    

    #うんちについて整形
    unchies = organize_unchi(unchi)

    #おなかの状態について整形
    withouts = organize_with(without)

    #生活についての整形
    lifes = organize_life(life)

    #体調についての整形
    condits = organize_cond(condit)
    
    #seleniumオプション
    def options():
        selen.options.add_argument("-window-size=1920,1080")
        selen.options.add_experimental_option("detach", True)#終わったときにブラウザを表示したままにする
        selen.options.add_argument("--headless=new")#非表示モード
        #selen.options.add_argument("--blink-settings=imagesEnabled=false")#画像非表示

        return selen.options
    
    
    
    #ドライバ起動----
    sc = selen(options())

    sc.tabs(URL_base).ovw()


    #ログイン----
    sc.find(xpaths["ID"]).send(user_data["clinical_ID"])
    sc.find(xpaths["PW"]).send(user_data["clinical_PW"])
    sc.find(xpaths["LG"]).click()


    #入力状況一覧を取得する----
    Input_Status = []
    for i in range(1,8):
        xpath = xpaths["Table"].format(i)

        Input_Status.append(sc.data(xpath).text().split())

    #Input_Status >>[
    #   ['2024/05/12', '(日)', '-'],
    #   ['2024/05/13', '(月)', '〇'],
    #   ['2024/05/14', '(火)', 'Today', '未入力'],
    #   ['2024/05/15', '(水)', '未入力'],
    #   ['2024/05/16', '(木)', '未入力'],
    #   ['2024/05/17', '(金)', '未入力'],
    #   ['2024/05/18', '(土)', '未入力']
    #]

    #前日分の入力状況を取得する----
    xpath = verify(Input_Status)

    #xpath >> //*[@id="nav-calendar"]/div/div[2]/div/table/tbody/tr[3]/td[2]/div/button if 前日分まで入力 else エラー(前日分までが入力されていません)


    #入力先に移動する----
    sc.find(xpath).click()

                
    #本当の入力URLを取得する----
    True_URL = sc.data('//*[@id="ifr"]').attribute("src")
    sc.tabs(True_URL).ovw()
    
    
    #入力開始----
 
    #排便時
    loop_inputer(sc,unchies)
    
    #排便時以外
    with_inputer(sc,withouts)
    
    #研究食品
    base = xpaths["reserc"]
    xpath1 , xpath2 = base["incu_tf"] , base["amoun_tt"]
    sc.find(xpath1).click()
    sc.find(xpath2).click()
    
    #生活について
    life_inputer(sc,lifes)
    
    #体調について
    cond_inputer(sc,condits)
    
    #保存する
    xpath = xpaths["savean"]
    sc.find(xpath).click()
    
    #終了
    sc.end()
  


if __name__ == "__main__":
        print("start")
        
        unchi = "0021 1.3 n 1 -1 2 1"
        #形式
        #時刻　量  性状(+3=柔、-3=硬) 色(+1=黒、-4=薄) 匂い(+2=強、-2=弱) 残便感(+3=有、0=無) 痛み(0=無、-3=有)
        #改行で複数回に対応
        
        without = "n 1 2"
        #形式
        #膨満(0=無、+5=強)　腹鳴(0=無、+5=強)　ガス(0=無、+5=強)
        
        life = "種類,量 1234 7.6 頻度,量"
        #形式
        #酒の種類,量　歩数 睡眠時間(0.5) 頻度を変えないやつ,量
        
        condit = "症状,原因,1 病院の原因"
        #形式
        #体調不良の内容(何時から何時),原因,頻度(0=頻繁,4=ほぼなし) 病院に行った場合は原因
        
        from modules.data_Roader import roader
        
        main(roader() , unchi,without,life,condit)

