"""
Playwright-based automation for 鵜の木球技場 reservation system.
Replaces: res.py, res_check.py, winning_check.py
"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

BASE_URL = "https://www.yoyaku.city.ota.tokyo.jp/"


def _parse_accounts(text):
    accounts = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(',')
        if len(parts) >= 2:
            accounts.append((parts[0].strip(), parts[1].strip()))
    return accounts


def _parse_dates(text):
    dates = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            dates.append(line)
    return dates


def _get_time_part(month_str, hour_str):
    month = int(month_str)
    if month in [11, 12, 1]:
        mapping = {'08': 2, '09': 2, '10': 3, '11': 3, '12': 4,
                   '13': 4, '14': 5, '15': 5, '16': 6}
    else:
        mapping = {'06': 2, '07': 2, '08': 3, '09': 3, '10': 4,
                   '11': 4, '12': 5, '13': 5, '14': 6, '15': 6, '16': 7}
    return mapping.get(hour_str)


def _log(q, msg, msg_type='info'):
    q.put({'type': msg_type, 'message': msg})


def _login(page, account_id, password, q):
    _log(q, f'  ログイン中: {account_id}')
    page.goto(BASE_URL)
    page.wait_for_load_state('networkidle')
    page.fill('#txtRiyoshaCode', account_id)
    page.fill('#txtPassWord', password)
    page.click('xpath=/html/body/main/div/form/div[1]/div/button')
    page.wait_for_load_state('networkidle')


def _logout(page, q):
    _log(q, '  ログアウト中...')
    try:
        page.click('xpath=//*[@id="contents_top"]/header/nav/a[2]')
        page.wait_for_load_state('networkidle')
    except Exception:
        pass


def _new_browser(playwright):
    return playwright.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
    )


# ---------------------------------------------------------------------------
# 1. 抽選予約申し込み (res.py 相当)
# ---------------------------------------------------------------------------
def run_reserve(account_text, date_text, log_queue):
    accounts = _parse_accounts(account_text)
    dates = _parse_dates(date_text)

    if not accounts:
        _log(log_queue, 'アカウントが入力されていません', 'error')
        log_queue.put({'type': 'done'})
        return
    if not dates:
        _log(log_queue, '日時リストが入力されていません', 'error')
        log_queue.put({'type': 'done'})
        return

    _log(log_queue, f'{len(accounts)} アカウント × {len(dates)} 日時の予約申し込みを開始します')

    with sync_playwright() as p:
        browser = _new_browser(p)

        for i, (account_id, password) in enumerate(accounts):
            _log(log_queue, f'\n[{i + 1}/{len(accounts)}] アカウント: {account_id}')
            page = browser.new_page()
            try:
                _login(page, account_id, password, log_queue)

                # 抽選申し込みを選択
                page.click('xpath=/html/body/main/div/form/div[4]/ul/li[1]/div[2]/ul/li[2]/label')
                page.wait_for_timeout(1000)

                # 大田区公園グループを選択
                page.click('xpath=/html/body/main/div/form/div[4]/ul/li[3]/div[2]/ul/li[4]/label')
                page.wait_for_timeout(1000)

                # 選択した条件で次へ
                page.click('#submitbutton')
                page.wait_for_load_state('networkidle')

                # 蒲田地域サッカー場
                page.click('#lu131113_001_52')
                page.wait_for_load_state('networkidle')

                # 鵜の木球技場をチェック
                page.click('#r_record20')
                page.wait_for_timeout(1000)

                # 選択した施設で検索
                page.click('#submitbutton')
                page.wait_for_load_state('networkidle')

                # 日時ループ
                for j, date_str in enumerate(dates):
                    _log(log_queue, f'  [{j + 1}/{len(dates)}] {date_str} 処理中...')
                    try:
                        columns = date_str.split('_')
                        date_part = columns[0]
                        hour_str = columns[1]
                        day = str(int(date_part[-2:]))
                        month_str = date_part[4:6]
                        time_part = _get_time_part(month_str, hour_str)

                        if time_part is None:
                            _log(log_queue, f'    時間枠が見つかりません: {hour_str}', 'warning')
                            continue

                        # 31日間
                        page.click('xpath=/html/body/form[2]/main/div[3]/div[2]/div[3]/ul/li[2]/fieldset/ul/li[2]/label')
                        page.wait_for_timeout(1000)

                        # 選択した条件で表示
                        page.click('xpath=/html/body/form[2]/main/div[3]/div[2]/div[3]/button')
                        page.wait_for_timeout(1000)

                        # 選択した条件で表示する
                        page.click('xpath=/html/body/form[2]/main/div[3]/div[2]/div[3]/div/div/button[1]')
                        page.wait_for_timeout(1000)

                        # 日時セルをクリック
                        xpath = (f'/html/body/form[2]/main/div[3]/div[2]/div[4]/ul/li'
                                 f'/div[3]/table/tbody/tr[{time_part}]/td[{day}]/label')
                        page.click(f'xpath={xpath}')
                        page.wait_for_timeout(1000)

                        # 選択した区分で次へ進む
                        page.click('#submitbutton')
                        page.wait_for_load_state('networkidle')

                        # 申し込み内容確定
                        page.click('xpath=/html/body/form[2]/main/div[3]/div/div[3]/button')
                        page.wait_for_load_state('networkidle')
                        page.wait_for_timeout(3000)

                        # 抽選申し込みを続ける
                        page.click('xpath=/html/body/form[2]/main/div[3]/div[2]/button[1]')
                        page.wait_for_load_state('networkidle')

                        _log(log_queue, f'    申し込み完了', 'success')

                    except Exception as e:
                        _log(log_queue, f'    エラー: {e}', 'error')
                        continue

                _logout(page, log_queue)
                _log(log_queue, f'  アカウント {account_id} 完了', 'success')

            except Exception as e:
                _log(log_queue, f'  エラー: {e}', 'error')
            finally:
                page.close()

        browser.close()

    _log(log_queue, '\n全処理が完了しました', 'success')
    log_queue.put({'type': 'done'})


# ---------------------------------------------------------------------------
# 2. 予約確認 + スクリーンショット (res_check.py 相当)
# ---------------------------------------------------------------------------
def run_check(account_text, screenshot_dir, log_queue):
    accounts = _parse_accounts(account_text)

    if not accounts:
        _log(log_queue, 'アカウントが入力されていません', 'error')
        log_queue.put({'type': 'done'})
        return

    _log(log_queue, f'{len(accounts)} アカウントの予約確認を開始します')
    Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
    screenshots = []

    with sync_playwright() as p:
        browser = _new_browser(p)

        for i, (account_id, password) in enumerate(accounts):
            _log(log_queue, f'\n[{i + 1}/{len(accounts)}] アカウント: {account_id}')
            page = browser.new_page()
            try:
                _login(page, account_id, password, log_queue)

                # マイページ
                page.click('xpath=//*[@id="formMain"]/div[1]/div/button')
                page.wait_for_load_state('networkidle')

                # 抽選申し込み内容
                page.click('xpath=//*[@id="formMain"]/main/div[2]/div[1]/table/tbody/tr/td[2]/table/tbody/tr/td[2]')
                page.wait_for_load_state('networkidle')

                # 大田区 公園グループ
                page.click('xpath=//*[@id="formMain"]/main/div[3]/div[1]/div/table/tbody/tr[3]/td[2]/span')
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(3000)

                # スクリーンショット
                filename = f'{account_id}.png'
                filepath = os.path.join(screenshot_dir, filename)
                page.screenshot(path=filepath, full_page=True)
                screenshots.append(filename)
                _log(log_queue, f'  スクリーンショット保存: {filename}', 'success')

                _logout(page, log_queue)

            except Exception as e:
                _log(log_queue, f'  エラー: {e}', 'error')
            finally:
                page.close()

        browser.close()

    log_queue.put({'type': 'screenshots', 'files': screenshots})
    _log(log_queue, '\n全処理が完了しました', 'success')
    log_queue.put({'type': 'done'})


# ---------------------------------------------------------------------------
# 3. 当選確認・予約確定 (winning_check.py 相当)
# ---------------------------------------------------------------------------
def run_winning(account_text, log_queue):
    accounts = _parse_accounts(account_text)

    if not accounts:
        _log(log_queue, 'アカウントが入力されていません', 'error')
        log_queue.put({'type': 'done'})
        return

    _log(log_queue, f'{len(accounts)} アカウントの当選確認を開始します')

    with sync_playwright() as p:
        browser = _new_browser(p)

        for i, (account_id, password) in enumerate(accounts):
            _log(log_queue, f'\n[{i + 1}/{len(accounts)}] アカウント: {account_id}')
            page = browser.new_page()
            try:
                _login(page, account_id, password, log_queue)

                confirmed = 0
                for attempt in range(20):  # 最大20件まで安全ループ
                    try:
                        # マイページへ
                        page.click('xpath=//*[@id="formMain"]/div[1]/div/button')
                        page.wait_for_load_state('networkidle')

                        # 抽選申し込み内容
                        page.click('xpath=//*[@id="formMain"]/main/div[2]/div[1]/table/tbody/tr/td[2]/table/tbody/tr/td[2]')
                        page.wait_for_load_state('networkidle')

                        # 大田区 公園グループ
                        page.click('xpath=//*[@id="formMain"]/main/div[3]/div[1]/div/table/tbody/tr[3]/td[2]/span')
                        page.wait_for_load_state('networkidle')
                        page.wait_for_timeout(5000)

                        # 当選要素を探す
                        parent = page.locator('xpath=/html/body/div/form[2]/main/div[3]/div')
                        winning_links = parent.get_by_text('当選').all()

                        if not winning_links:
                            _log(log_queue, '  当選件数: 0（未当選または処理済み）')
                            break

                        _log(log_queue, f'  当選件数: {len(winning_links)}件（最初の1件を処理します）')
                        winning_links[0].click()
                        page.wait_for_load_state('networkidle')
                        page.wait_for_timeout(3000)

                        # 利用規約の確認
                        page.click('xpath=/html/body/div/form[2]/main/div[3]/div/div[2]/button')
                        page.wait_for_load_state('networkidle')
                        page.wait_for_timeout(3000)

                        # 利用規約を承認
                        page.click('#chkRiyoKiyaku')

                        # 申し込みを確定
                        page.click('xpath=/html/body/form[2]/main/div[3]/div/div[3]/button')
                        page.wait_for_load_state('networkidle')
                        page.wait_for_timeout(3000)

                        confirmed += 1
                        _log(log_queue, f'  予約確定 {confirmed}件目', 'success')

                    except PlaywrightTimeoutError:
                        _log(log_queue, '  タイムアウト。次の試みに進みます', 'warning')
                        break
                    except Exception as e:
                        _log(log_queue, f'  当選処理エラー: {e}', 'error')
                        break

                _log(log_queue, f'  確定件数: {confirmed}件')
                _logout(page, log_queue)

            except Exception as e:
                _log(log_queue, f'  エラー: {e}', 'error')
            finally:
                page.close()

        browser.close()

    _log(log_queue, '\n全処理が完了しました', 'success')
    log_queue.put({'type': 'done'})
