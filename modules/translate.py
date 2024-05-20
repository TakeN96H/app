import requests
import re

#pycatchがウザいので生成停止
from sys import dont_write_bytecode;dont_write_bytecode = True

class _DeepL:
    def __init__(self,user_data):

        self.API_key = user_data["DeepL_API"]

    def translate(self, text, langage = "JA"):
        api = "https://api-free.deepl.com/v2/translate"

        auth_key = self.API_key

        #テキストの改行を全消去して良くする
        text = re.sub(r"\n","",text)
        print(text)

        #ヘッダー
        headers = {
        'Authorization': f'DeepL-Auth-Key {auth_key}'
        }

        #データ
        data = {
        "text": text,
        "target_lang" :langage
        }

        #リクエストする
        res = requests.post(api, data=data,headers=headers)

        #ステータスコード正常なときのみ出力
        if(res.status_code == 200):
            response = res.json()["translations"][0]["text"]
    
        else:
            print(f"エラー：{res.status_code}")

            response = "エラー"
    
        return response
    #使用状況を出力する
    def usage(self):
        api = "https://api-free.deepl.com/v2/usage"

        #ヘッダー
        headers = {
        'Authorization': f'DeepL-Auth-Key {self.API_key}'
        }

        #リクエストする
        res = requests.get(api,headers=headers)

        #ステータスコード正常なときのみ出力
        if(res.status_code == 200):

            count = res.json()["character_count"]
            limit = res.json()["character_limit"]

            #割合を出し，小数点以下3ケタで切り捨てる
            logic = str(res.json()["character_count"] / res.json()["character_limit"])[0:5]

            #型を統一するためfloatにする
            percent = float(logic)

            response =  count , limit , percent
    
        else:
            print(f"エラー：{res.status_code}")

            response =  0,0,0
    
        return response
        
        


if __name__ == "__main__" :
    from data_Roader import roader
    DeepL = _DeepL(roader())

    text = r"However, although the coverage is as comprehensive as possible, the distinction is emphasized among (a) instruments that are current and in common use; (b) instruments that are current but not widely used except in special applications, for reasons of cost or limited capabilities; and (c) instruments that are largely obsolete as regards new industrial implementations, but which are still encountered on older plant that was installed some years ago."

    result = DeepL.translate(text)

    print(result)


