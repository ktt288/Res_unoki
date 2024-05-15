import os
import re
import signal
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

if __name__ == "__main__":

    try:
        # Chromeのオプションを設定してヘッドレスモードを有効にする
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        # ヘッドレスブラウザでWebDriverを初期化
        driver = webdriver.Chrome(options=chrome_options)
        driver_ver = driver.capabilities["chrome"]["chromedriverVersion"]
        browser_ver = driver.capabilities["browserVersion"]
        if driver_ver.split(".")[0] != browser_ver.split(".")[0]:
            print("Chromedriver:", driver_ver.split(" ")[0])
            print("Chrome      :", browser_ver)
            raise ValueError(
                "The version of ChromeDriver needs to be the same as that of Chrome."
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

                    # 抽選申し込みボタンを押す
                    driver.find_element(
                        by=By.XPATH,
                        value="/html/body/main/div/form/div[4]/ul/li[1]/div[2]/ul/li[2]/label",
                    ).click()
                    time.sleep(1)

                    # 大田区公園グループボタンを押す
                    driver.find_element(
                        by=By.XPATH,
                        value="/html/body/main/div/form/div[4]/ul/li[3]/div[2]/ul/li[4]/label",
                    ).click()
                    time.sleep(1)

                    # 選択した条件で次へボタンを押す
                    driver.find_element(
                        by=By.XPATH,
                        value='//*[@id="submitbutton"]',
                    ).click()
                    time.sleep(3)

                    # 蒲田地域サッカー場ボタンを押す
                    driver.find_element(
                        by=By.XPATH,
                        value='//*[@id="lu131113_001_52"]',
                    ).click()
                    time.sleep(3)

                    # 鵜の木球技場をチェック
                    driver.find_element(
                        by=By.XPATH,
                        value='//*[@id="r_record20"]',
                    ).click()
                    time.sleep(1)

                    # 選択した施設で検索ボタンを押す
                    driver.find_element(
                        by=By.XPATH,
                        value='//*[@id="submitbutton"]',
                    ).click()
                    time.sleep(3)

                    # ここから日時ループ。
                    filename = 'datelist.txt'
                    # ファイルを開く
                    with open(filename, 'r', encoding='utf-8') as file:
                        # ファイルの各行を順番に読み取り
                        for line in file:
                            # 行末の改行文字を削除
                            line = line.strip()
                            # _で区切る。
                            columns = line.split('_')
                            # 何日？をlast_two_digitsに格納する。
                            first_column = columns[0]
                            last_two_digits = first_column[-2:]
                            if last_two_digits[0] == '0':
                                last_two_digits = last_two_digits[1]

                            # 何枠目？をtime_partに格納する。
                            time_part = None
                            # 条件分岐を使用して変数をセット
                            if columns[1] == '06':
                                time_part = 2
                            elif columns[1] == '08':
                                time_part = 3
                            elif columns[1] == '10':
                                time_part = 4
                            elif columns[1] == '12':
                                time_part = 5
                            elif columns[1] == '14':
                                time_part = 6
                            elif columns[1] == '16':
                                time_part = 7
                            else:
                                # 条件に該当しない場合、デフォルト値をセットする
                                time_part = None  # 必要に応じて他の値に変更

                            # 31日間 ボタンを押す
                            driver.find_element(
                                by=By.XPATH,
                                value='/html/body/form[2]/main/div[3]/div[1]/div[3]/ul/li[2]/fieldset/ul/li[2]/label',
                            ).click()
                            time.sleep(1)

                            # 選択した条件で表示 ボタンを押す
                            driver.find_element(
                                by=By.XPATH,
                                value='/html/body/form[2]/main/div[3]/div[1]/div[3]/button',
                            ).click()
                            time.sleep(1)

                            # 選択した条件で表示する ボタンを押す
                            driver.find_element(
                                by=By.XPATH,
                                value='/html/body/form[2]/main/div[3]/div[1]/div[3]/div/div/button[1]',
                            ).click()
                            time.sleep(1)

                            # 日時ボタンを押す
                            driver.find_element(
                                by=By.XPATH,
                                value='/html/body/form[2]/main/div[3]/div[1]/div[4]/ul/li/div[2]/table/tbody/tr[' + str(time_part) + ']/td[' + str(last_two_digits) + ']/label',
                            ).click()
                            time.sleep(1)

                            # 選択した区分で次へ進むボタンを押す
                            driver.find_element(
                                by=By.XPATH,
                                value='//*[@id="submitbutton"]',
                            ).click()
                            time.sleep(3)

                            # 申し込み内容確定ボタンを押す
                            driver.find_element(
                                by=By.XPATH,
                                value='/html/body/form[2]/main/div[3]/div/div[3]/button',
                            ).click()
                            time.sleep(3)

                            # 抽選申し込みを続けるボタンを押す
                            driver.find_element(
                                by=By.XPATH,
                                value='/html/body/form[2]/main/div[3]/div[3]/button[1]',
                            ).click()
                            time.sleep(3)

                    # 日時ループここまで。
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
