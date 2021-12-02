import os
from datetime import datetime as dt, timedelta as td
import psycopg2

# Gspread関連ライブラリ設定
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 使用APIの指定
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
# 認証情報設定
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    str(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]), scope
)
# OAuth2の資格情報を使用してGoogle APIにログイン
gc = gspread.authorize(credentials)
# 共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納
SPREADSHEET_KEY = str(os.environ["SPREADSHEET_KEY"])
# 共有設定したスプレッドシートのシート1を開く
worksheet = gc.open_by_key(SPREADSHEET_KEY).sheet1
# 共有設定したスプレッドシートのシート2を開く
worksheet2 = gc.open_by_key(SPREADSHEET_KEY).worksheet("match")


# データベースに接続
def get_connection():
    dsn = os.environ.get("DATABASE_URL")
    return psycopg2.connect(dsn)


# レギオンリーグ開催中かどうかを判定する
# return boolean (True)
def get_league_period():
    dt_now = dt.now() + td(hours=+0)
    league_start = dt.strptime(worksheet.acell("B12").value, "%Y-%m-%d %H:%M:%S")
    league_end = dt.strptime(worksheet.acell("C12").value, "%Y-%m-%d %H:%M:%S")
    if league_start < dt_now < league_end:
        return True
    else:
        return False


# match_records,match_records2の勝敗を返す
def judge_results(result):
    if result[4] == -1:
        judge = "敗北"
    elif result[4] == 1:
        judge = "勝利"
    else:
        judge = "引分けかデータ不良"
    return judge


# 　引数ありでSELECT文を実行し結果を1件取得する
def select_sql_with_param_fetch(sql, param):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, param)
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result


# 　引数ありでSELECT文を実行し結果を全件取得する
def select_sql_with_param_fetchall(sql, param):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, param)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results


# 引数なしでSELECT文を実行し結果を1件取得する
def select_sql_without_param_fetch(sql):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result


# 引数なしでSELECT文を実行し結果を全件取得する
def select_sql_without_param_fetchall(sql):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results
