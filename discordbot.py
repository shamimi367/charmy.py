import discord
from discord.ext import commands, tasks
import os
import traceback
import psycopg2
from datetime import datetime as dt, timedelta as td, timezone as tz
import cogs.event as ev
import functions as fnc
import cogs.legion as leg

# 読み込むコグの名前を格納しておく。
INITIAL_EXTENSIONS = [
    "cogs.reminder",
    "cogs.birthday",
    "cogs.event",
    "cogs.match",
    "cogs.skill",
    "cogs.help",
    "cogs.vchat",
    "cogs.legion",
]

discord_intents = discord.Intents.all()
discord_intents.members = True

# メンションにも反応するように変更
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("/"),
    intents=discord_intents,
    help_command=None,
)

for cog in INITIAL_EXTENSIONS:
    try:
        bot.load_extension(cog)
    except Exception:
        traceback.print_exc()

# 環境変数からトークンを取得
TOKEN = os.environ["DISCORD_BOT_TOKEN"]
# 環境変数からBot管理者IDを取得
ADMIN_ID = os.environ["ADMIN_ID"]
# 環境変数から投稿先チャンネルを設定
# 本番用テキストチャンネル
CHANNEL_ID = int(os.environ["PERFORMANCE_CHANNEL"])
# 管理用クローズドチャンネル
TEST_ID = int(os.environ["TEST_CHANNEL"])
# ログ出力用チャンネル
LOG_ID = int(os.environ["LOG_CHANNEL"])
# 作戦用チャンネル
STR_ID = int(os.environ["STRATEGY_CHANNEL"])
# 作戦まとめチャンネル
MATOME_ID = int(os.environ["MATOME_CHANNEL"])
# タイムゾーンの生成
JST = tz(td(hours=+9), "JST")

######################################
#  ここからゲーム内に関わる設定項目(Dynosインスタンス起動時に取得)
#
# レギオンマッチの開催曜日(Mon~Sun)
# LM => レギオンマッチ　LL =>レギオンリーグ
LM = ["Wed", "Sat"]

# イベント開催情報
event1_name = event1_date = event1_medal = ""
event2_name = event2_date = event2_medal = ""
gacha1_name = gacha1_expiry = gacha2_name = gacha2_expiry = ""

######################################
# ここから定時発言用のループ処理を開始
ev.set_event_data()
ev.set_gacha_data()


# 60秒に一回ループ
@tasks.loop(seconds=60)
async def loop():
    dt_now = dt.now(JST)
    dtday = dt_now.date()
    now = dt.now(JST).strftime("%H:%M")
    now_m = dt.now(JST).strftime("%M")
    now_d = dt.now(JST).strftime("%d")
    wd = dt_now.strftime("%a")
    channel = bot.get_channel(CHANNEL_ID)

    # 毎時00分の時にのみ実行判定する処理
    if now_m == "00":
        # TODO:リマインダーの終了n時間前に通知する

        # メンテナンス開始1時間前に告知する
        maintenance_date = fnc.worksheet.acell("B9").value
        try:
            dt_man = dt.strptime(maintenance_date, "%Y-%m-%d %H:%M:%S")
        except ValueError as ve:
            channel = bot.get_channel(TEST_ID)
            await channel.send("ERROR:" + str(ve))
            return
        if dt_now.date() == dt_man.date():
            dt_man_before = dt_man + td(hours=-1)
            if now == dt_man_before.strftime("%H:%M"):
                fmt_mnt = dt.strftime(dt_man, "%H時")
                await channel.send(
                    "{}から17時までメンテナンスがあるよ!APの残りに注意しようね。\n"
                    "終了時刻は念のため公式Twitterを確認しようね!".format(fmt_mnt)
                )

        # イベント終了1時間前に告知する
        current_event = ev.get_event_data()
        events = ev.get_all_events()
        if current_event is not None:
            try:
                dt_event = current_event[1]
                ev1_medal = events[2]
                ev2_medal = events[5]
                if dt_now.date() == dt_event.date():
                    dt_event_before = dt_event + td(hours=-1)
                    if now == dt_event_before.strftime("%H:%M"):
                        fmt_end_time = dt_event.strftime("%H時%M分")
                        await channel.send(
                            "イベント『{0}』は今日の{1}までだよ!\n欲しい報酬は全部取れたかな?".format(
                                current_event[0], fmt_end_time
                            )
                        )
                if dt_now.date() == ev1_medal.date():
                    ev1_medal_before = ev1_medal + td(hours=-1)
                    if now == ev1_medal_before.strftime("%H:%M"):
                        fmt_mdl1 = dt.strftime(ev1_medal, "%H時%M分")
                        await channel.send(
                            "{0}メダルの交換期限は今日の{1}までだよ!忘れずにアイテムと交換しようね!".format(
                                events[0], fmt_mdl1
                            )
                        )
                elif dt_now.date() == ev2_medal.date():
                    ev2_medal_before = ev2_medal + td(hours=-1)
                    if now == ev2_medal_before.strftime("%H:%M"):
                        fmt_mdl2 = dt.strftime(ev2_medal, "%H時%M分")
                        await channel.send(
                            "{0}メダルの交換期限は今日の{1}までだよ!忘れずにアイテムと交換しようね!".format(
                                events[3], fmt_mdl2
                            )
                        )
            except Exception as ve:
                channel = bot.get_channel(TEST_ID)
                await channel.send("ERROR:" + str(ve))
                return

    if now == "09:00":
        if fnc.get_league_period():
            await channel.send("レギオンリーグ開催中だよ！対戦相手を確認して作戦を話し合おうね!")
        elif wd in LM:
            await channel.send("おはよー9時だよ☆\n今日は23時からレギオンマッチだよ!\n対戦相手を確認して作戦を話し合おうね!")
        sql = "SELECT name, birth_day FROM characters WHERE %s <= birth_day ORDER BY birth_day LIMIT 1;"
        result = fnc.select_sql_with_param_fetch(sql, (dtday,))
        birth_day = result[1].strftime("%-m月%-d日")
        if dtday == result[1]:
            await channel.send(
                "今日" + birth_day + "は、" + result[0] + "さまの誕生日だよ!みんなでお祝いしようね!"
            )
        # リマインダー取得処理
        sql = "SELECT * FROM reminders WHERE %s <= end_time ORDER BY end_time;"
        results = fnc.select_sql_with_param_fetchall(sql, (dtday,))
        if len(results) == 0:
            return
        elif results[0] is None:
            return
        else:
            for i in range(len(results)):
                if dtday == results[i][3].date():
                    userid = int(results[i][1])
                    user = bot.get_user(userid)
                    try:
                        await user.send(
                            "『"
                            + results[i][2]
                            + "』の期限は今日までだよ!\n忘れずに確認しようね!\n"
                            + "設定期限 ["
                            + results[i][3].strftime("%Y/%m/%d %H:%M")
                            + "]"
                        )
                    except NameError:
                        await channel.send(
                            "<@"
                            + str(results[i][1])
                            + ">\nDMに通知できなかったリマインダー["
                            + str(results[i][0])
                            + "]があるよ!"
                        )
    elif now == "11:00":
        current_event = ev.get_event_data()
        if current_event is not None:
            print("[INFO] Current Event:" + current_event[0])
        else:
            channel = bot.get_channel(TEST_ID)
            print("[Error] Event Data Not Found!")
            await channel.send("イベントデータが取得出来ていません")

    elif now == "22:00":
        if fnc.get_league_period() or wd in LM:
            await channel.send("22時だよ☆\n今日は23時からレギオンマッチだよ!\n作戦をチェックして編成を確認しようね!")
            # 2021/11/03ゲーム内不具合解消済みにつき削除
            # await channel.send("サブユニットは編成のリリィが変わるとリセットされるから気をつけようね!")
        else:
            await channel.send("22時だよ☆\n今日は23時15分から外征任務をやろうね!")
        ev.set_gacha_data()
        gacha_data = ev.get_gacha_data()
        try:
            gc1_expiry = gacha_data[1]
            gc2_expiry = gacha_data[3]

            if dt_now.date() == gc1_expiry.date():
                fmt_gacha1 = dt.strftime(gc1_expiry, "%H時%M分")
                await channel.send(
                    "{0}の交換期限は今日の{1}までだよ!忘れずにメモリアと交換しようね!".format(
                        gacha_data[0], fmt_gacha1
                    )
                )
            elif dt_now.date() == gc2_expiry.date():
                fmt_gacha2 = dt.strftime(gc2_expiry, "%H時%M分")
                await channel.send(
                    "{0}の交換期限は今日の{1}までだよ!忘れずにメモリアと交換しようね!".format(
                        gacha_data[2], fmt_gacha2
                    )
                )
        except ValueError as ve:
            channel = bot.get_channel(TEST_ID)
            await channel.send("ERROR:" + str(ve))
            return
    elif now == "22:30":
        if fnc.get_league_period() or wd in LM:
            # スプシ内を検査する、未入力なら投稿を促す
            channel = bot.get_channel(STR_ID)
            ss_chk = fnc.worksheet2.acell("E6").value
            if ss_chk is None:
                await channel.send("<@" + ADMIN_ID + ">\nスプレッドシートに未入力の項目があるよ")
    elif now == "22:45":
        if fnc.get_league_period() or wd in LM:
            # レギリ相手の自動投稿処理
            ss_posted = fnc.worksheet2.acell("F6").value
            channel = bot.get_channel(MATOME_ID)
            if ss_posted is None:
                # matchシート内の文字列を抽出して辞書を作成
                ss_dic = leg.get_legion()
                # レギオン情報登録処理
                # レギオンテーブルのレコード存在確認
                comment = leg.exist_legion(ss_dic)
                embed = leg.embed_legion(ss_dic)
                await channel.send("@everyone\n今日の対戦相手と作戦を確認しようね！")
                await channel.send(embed=embed)
                await channel.send(comment)
                fnc.worksheet2.update_acell("F6", "OK")

    elif now == "00:30":
        # 管理用テストデータの出力
        error = False
        channel = bot.get_channel(TEST_ID)
        event_data = ev.get_event_data()
        await channel.send("TEST CODE OUTPUT...")
        dt_now = dt.now(JST)
        await channel.send("START:" + str(dt_now) + "...")
        maintenance_date = fnc.worksheet.acell("B9").value
        try:
            dt_man = dt.strptime(maintenance_date, "%Y-%m-%d %H:%M:%S")
            await channel.send("定期メンテ設定日" + str(dt_man))
        except ValueError as ve:
            error = True
            await channel.send("メンテナンス情報取得エラー")
            await channel.send(ve)
        if event_data is None:
            error = True
            await channel.send("イベントデータ取得エラー")
        else:
            await channel.send(
                "開催中イベント:『"
                + event_data[0]
                + "』 \nDate:"
                + str(event_data[1])
                + " Medal:"
                + str(event_data[2])
            )
        sql = "SELECT COUNT(name) FROM characters GROUP BY gd_cd ORDER BY gd_cd;"
        result = fnc.select_sql_without_param_fetchall(sql)
        if result is None:
            error = True
            await channel.send("リリィDB取得エラー")
        else:
            await channel.send(
                "DB登録済みリリィ\n　百合ヶ丘："
                + str(result[0][0])
                + "人　エレンスゲ："
                + str(result[1][0])
                + "人　神庭女子："
                + str(result[2][0])
                + "人"
            )
        sql = "SELECT COUNT(*) FROM reminders;"
        con_rem = fnc.select_sql_without_param_fetch(sql)
        if con_rem is None:
            error = True
            await channel.send("リマインダー取得エラー")
        else:
            await channel.send("登録済みリマインダー数：" + str(con_rem[0]) + "件")

        sql = "SELECT COUNT(*) FROM match_records;"
        con_match = fnc.select_sql_without_param_fetch(sql)
        if con_match is None:
            error = True
            await channel.send("戦績データ取得エラー")
        else:
            await channel.send("登録済み戦績数：" + str(con_match[0]) + "件")

        if fnc.get_league_period():
            await channel.send("レギオンリーグ：開催中")
        else:
            await channel.send("レギオンリーグ：非開催中")

        sql = "SELECT COUNT(*) FROM match_records2;"
        con_match2 = fnc.select_sql_without_param_fetch(sql)
        if con_match2 is None:
            error = True
            await channel.send("戦績データ取得エラー")
        else:
            await channel.send("登録済みリーグ戦績数：" + str(con_match2[0]) + "件")

        sql = "SELECT COUNT(*) FROM legions;"
        con_legion = fnc.select_sql_without_param_fetch(sql)
        if con_legion is None:
            error = True
            await channel.send("レギオンデータ取得エラー")
        else:
            await channel.send("DB登録済みレギオン数：" + str(con_legion[0]) + "件")

        await channel.send("ボイスチャット利用情報")
        if now_d == "01":
            # 毎月1日は前月分の合計データを表示する
            sql = """
                    SELECT
                        ch_id
                        , COUNT(*) AS 利用日数
                        , SUM(日次合計) AS 月間使用時間
                        , SUM(日次合計) / COUNT(*) AS 日平均利用時間
                    FROM
                        (
                            SELECT
                                ch_id
                                , TO_CHAR(entry_time, 'YYYY/MM/DD') AS 利用日
                                , MAX(duration) AS 日次合計
                            FROM
                                vc_logs
                            WHERE
                                DATE_PART('month', now()) - 1 = DATE_PART('month', entry_time)
                                AND EXTRACT(EPOCH FROM duration ::time) > 60
                            GROUP BY
                                ch_id
                                , 利用日
                            ORDER BY
                                利用日
                        ) daily_logs
                    GROUP BY
                        ch_id
                    ORDER BY
                        ch_id DESC;
                    """
        else:
            sql = """
                SELECT
                    ch_id
                    , COUNT(*) AS 利用日数
                    , SUM(日次合計) AS 月間使用時間
                    , SUM(日次合計) / COUNT(*) AS 日平均利用時間
                FROM
                    (
                        SELECT
                            ch_id
                            , TO_CHAR(entry_time, 'YYYY/MM/DD') AS 利用日
                            , MAX(duration) AS 日次合計
                        FROM
                            vc_logs
                        WHERE
                            DATE_PART('month', now()) = DATE_PART('month', entry_time)
                            AND EXTRACT(EPOCH FROM duration ::time) > 60
                        GROUP BY
                            ch_id
                            , 利用日
                        ORDER BY
                            利用日
                    ) daily_logs
                GROUP BY
                    ch_id
                ORDER BY
                    ch_id DESC;
                """
        vc_info = fnc.select_sql_without_param_fetchall(sql)
        if len(vc_info) != 0:
            # 使用時間を時分秒に変換する
            btl = ev.get_remain(vc_info[0][2])
            lb = ev.get_remain(vc_info[1][2])
            av_btl = ev.get_remain(vc_info[0][3])
            av_lb = ev.get_remain((vc_info[1][3]))
            await channel.send(
                "外征/レギマ：{0}時間{1}分{2}秒 ({3}時間{4}分{5}秒/日)".format(
                    btl[0], btl[1], btl[2], av_btl[0], av_btl[1], av_btl[2]
                )
            )
            await channel.send(
                "ロビー：{0}時間{1}分{2}秒 ({3}時間{4}分{5}秒/日)".format(
                    lb[0], lb[1], lb[2], av_lb[0], av_lb[1], av_lb[2]
                )
            )
            if now_d == "03":
                btl_time = btl[0] + ":" + btl[1] + ":" + btl[2]
                lb_time = lb[0] + ":" + lb[1] + ":" + lb[2]
                time = (btl_time, lb_time)
                try:
                    conn = fnc.get_connection()
                    for i in range(len(vc_info)):
                        cur = conn.cursor()
                        sql = (
                            "INSERT INTO vc_monthly_logs (month, ch_id, monthly_use_time) "
                            "VALUES ( TO_CHAR(CURRENT_DATE + CAST( '-7 days' AS INTERVAL ) , 'YYYY/MM'), %s, %s)"
                        )
                        cur.execute(sql, (str(vc_info[i][0]), time[i]))
                    conn.commit()
                    conn.close()
                    await channel.send("月間データが登録されました")
                except psycopg2.OperationalError as ve:
                    print(ve)
                    await channel.send("月間データ登録エラー")
                    error = True
        else:
            error = True
            await channel.send("ボイスチャット情報が取得できません")
        dt_now = dt.now(JST)
        await channel.send("FINISHED:" + str(dt_now) + "...")
        if error:
            await channel.send("正常に取得できていないデータがあります!ログを確認してください!")
        else:
            await channel.send("CHARMY bot systems are up and running!!")


# ループ処理実行
@bot.event
async def on_ready():
    print("CHARMY Bot System Started...")
    # for channel in bot.get_all_channels():
    #     print("----------")
    #     print("チャンネル名：" + str(channel.name))
    #     print("チャンネルID：" + str(channel.id))
    #     print("----------")
    loop.start()


@bot.event
async def on_command_error(ctx, error):
    channel = bot.get_channel(TEST_ID)
    orig_error = getattr(error, "original", error)
    error_msg = "".join(
        traceback.TracebackException.from_exception(orig_error).format()
    )
    await ctx.send("エラーが発生したよ!")
    await channel.send(error_msg)


bot.run(TOKEN)
