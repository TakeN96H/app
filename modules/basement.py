version = "1.0.1"
from sys import dont_write_bytecode;dont_write_bytecode = True


#ローカルアドレスとグローバルアドレスを出力
import os
import requests

def ip():

    Global_ip = requests.get('https://ifconfig.me').text

    expot={
        "Local_ip":"",
        "Global_ip":Global_ip
    }

    return expot

#現在のディレクトリのファイル&フォルダツリーを表示
def directory_tree(dir):
    from pathlib import Path
    path = Path(dir)
    contents = ""

    contents += f'+ {path.absolute()}\n'
    for entry in path.iterdir():
        if entry.is_dir():
             contents += directory_tree(entry)
        else:
             contents += f'  - {entry.name}\n'
    return contents

import datetime
class _logger:
    def __init__(self,path,debug =False) -> None:
        self.path = path
        self.debug = debug

    def logger(self,text):
        print(f"({self.path}):{text}")

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #改行で区切られていた場合
        midiate = text.split("\n")
        text = ""
        for elem in midiate:
            text += f"[{now}] {elem}\n"
        
        
        
        
        try:
            with open(self.path,"a",encoding='utf-8') as a:
                a.write(text)
        except FileNotFoundError:
            dir_name = os.path.dirname(self.path)

            #フォルダがあるかどうか検査
            if os.path.isdir(dir_name):
                pass
            else:
                os.mkdir(dir_name)
            
            with open(self.path,"w",encoding='utf-8') as w:
                w.write(text)
        
        return text

#作ったは良いが最初のimportの際にpathが通ってなければ使えないので意味ない説
def pather(dir_UP :int = 0):
    
    path1 = os.path.dirname(__file__)

    for i in range(dir_UP):
        print("aaa")
        path1 = os.path.dirname(path1)

    return path1


if __name__ == "__main__":
    print(ip())

    logger = _logger("D:/m.log").logger

    logger("abc")

    path1 = pather(0)

    print(path1)