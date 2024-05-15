import os
import re
import signal
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

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

                    # 画面キャプチャ
                    # ページ全体の高さを取得
                    page_height = driver.execute_script("return document.body.scrollHeight")

                    # キャプチャ用の高さを設定
                    driver.set_window_size(1080, page_height)
                    time.sleep(3)

                    # JavaScriptを実行してページのズームレベルを変更
                    driver.execute_script("document.body.style.zoom='33%'")

                    # キャプチャを取得し、ファイルに保存
                    file_name = f"{id}.png"
                    driver.save_screenshot(file_name)

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

