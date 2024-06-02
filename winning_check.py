import os
import re
import signal
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if __name__ == "__main__":

    try:
        driver = webdriver.Chrome()
        driver_ver = driver.capabilities["chrome"]["chromedriverVersion"]
        browser_ver = driver.capabilities["browserVersion"]
        if driver_ver.split(".")[0] != browser_ver.split(".")[0]:
            print("Chromedriver:", driver_ver.split(" ")[0])
            print("Chrome      :", browser_ver)
            raise ValueError(
                "The version of ChromeDriver need to be same with that of Chrome."
            )

        # アカウントループ開始！
        # ファイル名を指定
        filename = 'accountlist.csv'

        # ファイルを開く
        with open(filename, 'r', encoding='utf-8') as file:
            # ファイルの各行を順番に読み取り
            for line in file:
                try:
                    print("Starting new account loop...")
                    # 行末の改行文字を削除
                    line = line.strip()

                    # カンマで行を分割してカラムの値を取得
                    columns = line.split(',')

                    # ID/PASSを入力し、ログイン
                    id = columns[0]
                    password = columns[1]

                    # うぐいすねっとへアクセス
                    url_acc = "https://www.yoyaku.city.ota.tokyo.jp/"
                    driver.get(url_acc)
                    time.sleep(3)

                    # ID入力
                    driver.find_element(
                        by=By.XPATH,
                        value='//*[@id="txtRiyoshaCode"]',
                    ).send_keys(id)

                    # PASS入力
                    driver.find_element(
                        by=By.XPATH,
                        value='//*[@id="txtPassWord"]',
                    ).send_keys(password)

                    # ログインするボタンを押す
                    driver.find_element(
                        by=By.XPATH,
                        value="/html/body/main/div/form/div[1]/div/button",
                    ).click()
                    time.sleep(3)

                    # マイページボタンを押す
                    driver.find_element(
                        by=By.XPATH,
                        value='//*[@id="formMain"]/div[1]/div/button',
                    ).click()
                    time.sleep(1)

                    # 抽選申し込み内容ボタンを押す
                    driver.find_element(
                        by=By.XPATH,
                        value='//*[@id="formMain"]/main/div[2]/div[1]/table/tbody/tr/td[2]/table/tbody/tr/td[2]',
                    ).click()
                    time.sleep(1)

                    # 大田区 公園グループボタンを押す
                    driver.find_element(
                        by=By.XPATH,
                        value='//*[@id="formMain"]/main/div[3]/div[1]/div/table/tbody/tr[3]/td[2]/span',
                    ).click()
                    time.sleep(5)

                    # 抽選結果をチェックする。
                    # 検索対象の文言
                    text_to_find = "当選"
                    parent_xpath = "/html/body/div/form[2]/main/div[3]/div"

                    try:
                        # 親要素を取得
                        parent_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, parent_xpath))
                        )
                        # 文言を含むすべての要素を検索
                        elements = parent_element.find_elements(By.XPATH, f".//*[contains(text(), '{text_to_find}')]")
                        
                        # 各要素のXPathを取得
                        for index, element in enumerate(elements, start=1):
                            xpath = driver.execute_script("""
                                function getElementXPath(elt) {
                                    var path = "";
                                    for (; elt && elt.nodeType == 1; elt = elt.parentNode) {
                                        idx = getElementIdx(elt);
                                        xname = elt.tagName;
                                        if (idx > 1) xname += "[" + idx + "]";
                                        path = "/" + xname + path;
                                    }

                                    return path;
                                }

                                function getElementIdx(elt) {
                                    var count = 1;
                                    for (var sib = elt.previousSibling; sib ; sib = sib.previousSibling) {
                                        if(sib.nodeType == 1 && sib.tagName == elt.tagName) count++;
                                    }
                                    return count;
                                }

                                return getElementXPath(arguments[0]);
                            """, element)

                            print(f"文言 '{text_to_find}' を含む要素 {index} のXPath: {xpath}")
                            # 当選リンクをクリック
                            driver.find_element(
                                by=By.XPATH,
                                value=xpath,
                            ).click()
                            time.sleep(3)

                            # 利用規約の確認をクリック
                            driver.find_element(
                                by=By.XPATH,
                                value="/html/body/div/form[2]/main/div[3]/div/div[2]/button",
                            ).click()
                            time.sleep(3)

                            # 利用規約を承認する、をクリック
                            driver.find_element(
                                by=By.XPATH,
                                value='//*[@id="chkRiyoKiyaku"]',
                            ).click()

                            # 申し込みを確定をクリック
                            driver.find_element(
                                by=By.XPATH,
                                value="/html/body/form[2]/main/div[3]/div/div[3]/button",
                            ).click()
                            time.sleep(3)

                    except Exception as e:
                        print(f"Error: {e}")

                    # ログアウトボタンを押す
                    driver.find_element(
                        by=By.XPATH,
                        value='//*[@id="contents_top"]/header/nav/a[2]',
                    ).click()
                    time.sleep(3)
                    # Close Chrome window
                    if driver:
                        os.kill(driver.service.process.pid, signal.SIGTERM)
                except Exception as e:
                    print(f"Error in account loop: {e}")
                    continue  # 次のアカウントに進む
        # アカウントループここまで。
    except Exception as e:
        print(f"\nError: {e}")

