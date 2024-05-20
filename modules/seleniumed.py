version = "1.0.1"
from sys import dont_write_bytecode;dont_write_bytecode = True
from os.path import dirname
path = dirname(dirname(__file__))

#スレイピング系
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

#エラーキャッチ
import selenium.common.exceptions

#html解析系
from bs4 import BeautifulSoup
from lxml import html

from time import sleep as wait

from os.path import isfile , isdir

class MyErr(Exception):{}


class selen:
    #import時にオプションを指定するための布石
    options = webdriver.ChromeOptions()
    KEYS = Keys


    def __init__(self , options):
        
        options.add_argument("--disable-blink-features=AutomationControlled")#BOT対策
        options.add_experimental_option("excludeSwitches", ['enable-automation','enable-logging'])#chromeは現在自動制御...を止める，USB機器が....を止める
        
        #広告ブロック拡張機能
        if isfile(path + "/modules/uBlock-Origin.crx"):
            options.add_extension(path + "/modules/uBlock-Origin.crx")#広告ブロック

        #driverをグローバル変数に渡す
        global driver
        driver = webdriver.Chrome(options=options)

  
    #ページ内要素制御
    class find:
        def __init__(self , xpath):
            self.xpath = xpath

        #文字列を送る
        def send(self , value):
            count = 0
            while True:
                count += 1
                #見つけられるか試す
                try:
                    driver.find_element(By.XPATH , self.xpath).send_keys(value)
                    break

                except selenium.common.exceptions.NoSuchElementException :{} #見つからないエラー
                except selenium.common.exceptions.StaleElementReferenceException: {} #さっきまであったけど見つからなくなっちゃったエラー
                except selenium.common.exceptions.ElementNotInteractableException:{} #アクセス不能エラー

                #知らないエラー
                except Exception as err:
                    raise MyErr(str(err))
                finally:
                    wait(0.1)
                
                if 300 < count:
                    raise MyErr("NG, cant find an element for 30s.")

            return "OK"
        #キーボード入力を送る
        def keys(self , key):
            count = 0
            while True:
                count += 1
                #見つけられるか試す
                try:
                    driver.find_element(By.XPATH , self.xpath).send_keys(key)
                    break

                except selenium.common.exceptions.NoSuchElementException :{} #見つからないエラー
                except selenium.common.exceptions.StaleElementReferenceException: {} #さっきまであったけど見つからなくなっちゃったエラー
                except selenium.common.exceptions.ElementNotInteractableException:{} #アクセス不能エラー

                #知らないエラー
                except Exception as err:
                    raise MyErr(str(err))
                finally:
                    wait(0.1)

                if 300 < count:
                    raise MyErr("NG, cant find an element for 30s.")

            return "OK"
        #クリック
        def click(self):
            count = 0
            while True:
                count += 1
                #見つけられるか試す
                try:
                    driver.find_element(By.XPATH , self.xpath).click()
                    break

                except selenium.common.exceptions.NoSuchElementException :{} #見つからないエラー
                except selenium.common.exceptions.StaleElementReferenceException: {} #さっきまであったけど見つからなくなっちゃったエラー
                except selenium.common.exceptions.ElementNotInteractableException:{} #アクセス不能エラー

                #知らないエラー
                except Exception as err:
                    raise MyErr(str(err))
                finally:
                    wait(0.1)
                
                if 300 < count:
                    raise MyErr("NG, cant find an element for 30s.")

            return "OK"

    #タブ関連制御
    class tabs:
        def __init__(self , url=""):
            self.url = url

        #上書き
        def ovw(self):
            driver.get(self.url)

        #新しいタブ
        def new(self, switch = True):
            count = 0
            while True:
                try:
                    driver.execute_script(f"window.open('{self.url}')")

                    break
                except Exception:
                    driver.switch_to.window(driver.window_handles[0])
                    print("new miss")
                    count += 1
                    wait(0.25)

                if 30 < count:
                    raise MyErr('tabs cant open')

            if switch : driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])

            return "OK"

        #クッキー注入
        def cookie(self,cookies):
            for elem in cookies:
                driver.add_cookie(elem)

            return "OK"

        #更新
        def refresh(self):
            driver.refresh()
            return "OK"
        
        #現在のタブを閉じる
        def close(self):
            driver.close()
            return "OK"
        
        #現在のタブ数を返す
        def count(self):
            while True:
                try:
                    count = len(driver.window_handles)
                    break
                except Exception:{}
            
            return count
        
                
        #全画面にする
        def max(self):
            driver.maximize_window()
            return "OK"
        
        #最小化する
        def min(self):
            driver.minimize_window()
            return "OK"
        
        #動かす
        def move(self,x,y):
            
            if type(x) == int and type(y) == int is False:
                return "NG"

            driver.set_window_position(x,y)
            return "OK"


        #タブを移動する
        def switch(self,number):
            count = 0
            while True:
                try:
                    driver.switch_to.window(driver.window_handles[number])
                    break
                #範囲ミス
                except IndexError:
                    raise MyErr("out of tab number")
                except Exception as err:
                    print(err)
                
                count += 1
                if 300 < count:
                    raise MyErr("cant change tab")



    #データ関連制御
    class data:
        def __init__(self , xpath = "/html",limit = 120):
            self.xpath = xpath
            self.limit = limit
            self.html_data = driver.page_source

            #重複する=ロード完了まで待機
            count = 0
            while True:
                wait(0.1)
                if self.html_data == driver.page_source:
                    break
                
                self.html_data = driver.page_source
                count += 1
                if 50 < count:
                    raise MyErr("load time out")


        #単純にhtmlデータを返す
        def html_back(self):
            return self.html_data        

        #xpathの先にあるテキストデータを返す
        def text(self):
            
            #データにアクセスできるか確認
            count = 0
            while True:
                try:
                    driver.find_element(By.XPATH,self.xpath)
                    break
                except Exception:
                    if self.limit != 0 : wait(0.1)
                    count += 1

                if self.limit < count :
                    raise MyErr("cant find data by xpath")

                    
            soup = BeautifulSoup(self.html_data,"html.parser")
            lxml_data = html.fromstring(str(soup))
            
            #要素が見つからなかった場合は空の配列になるのでエラーを返す
            try:
                result = lxml_data.xpath(self.xpath)[0].text_content()
                return result
            except IndexError:
                raise MyErr("cant find data")

        #現在のurlを返す
        def url(self):
            return driver.current_url
        
        #attribute
        def attribute(self , attr = "outerHTML"):
            count = 0
            while True:
                count += 1
                #見つけられるか試す
                try:
                    result = driver.find_element(By.XPATH , self.xpath).get_attribute(attr)
                    break

                except selenium.common.exceptions.NoSuchElementException :{} #見つからないエラー
                except selenium.common.exceptions.StaleElementReferenceException: {} #さっきまであったけど見つからなくなっちゃったエラー
                except selenium.common.exceptions.ElementNotInteractableException:{} #アクセス不能エラー

                #知らないエラー
                except Exception as err:
                    raise MyErr(str(err))
                finally:
                    wait(0.1)
                
                if 300 < count:
                    raise MyErr("NG, cant find an element for 30s.")

            return result
        
    #終了させるやつ
    def end(NoN="None"):
        #引数がなぜか入ってしまうので対策
        driver.quit()





if __name__ == "__main__":
    def option():
        #オプション群---------------------
        selen.options.add_argument("-window-size=1280,720")
        selen.options.add_experimental_option("detach", True)#終わったときにブラウザを表示したままにする
        #selen.options.add_argument("--headless=new")#非表示モード
        selen.options.add_argument("--blink-settings=imagesEnabled=false")#画像非表示
        selen.options.add_argument("--no-sandbox")
        selen.options.add_argument("--disable-gpu")
        selen.options.add_argument("disable-dev-shm-usage")

        return selen.options

    sc = selen(option())

    sc.tabs("https://ejje.weblio.jp/").ovw()
    
    sc.find('//*[@id="searchWord"]').send("clock")
    
    sc.find('//*[@id="headFixBxTR"]/input').click()
    
    result = sc.data('//*[@id="summary"]/div[4]/p/span[2]').text().replace(" ","").replace("\n","")
    
    print(result)
    
    sc.end()
