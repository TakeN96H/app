#親ファイルにパスをつける
from os.path import dirname
path = dirname(dirname(__file__))


#pycatchがウザいので生成停止
from sys import dont_write_bytecode;dont_write_bytecode = True

#個人データをロードする
def roader():
    import json
    
    with open(path + "/data/secret.json",encoding="utf-8") as f:
        user_data = json.load(f)

    print("secret.json loaded.")

    return user_data


if __name__ == "__main__" :
    print(path)
    
    data = roader()

    print(data)


