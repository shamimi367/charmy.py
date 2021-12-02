from discord.ext import commands
import os
from datetime import datetime as dt, timedelta as td, timezone as tz
import psycopg2
import functions as fnc
import cogs.event as ev

# 本番用テキストチャンネル
CHANNEL_ID = int(os.environ["PERFORMANCE_CHANNEL"])
# 管理用クローズドチャンネル
TEST_ID = int(os.environ["TEST_CHANNEL"])
# ログ出力用クローズドチャンネル
LOG_ID = int(os.environ["LOG_CHANNEL"])

# タイムゾーンの生成
JST = tz(td(hours=+9), "JST")


class Vchat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    # Cogが読み込まれた時に発動
    async def on_ready(self):
        print("Load VChat module...")

    # ボイスチャット関連の情報取得
    @commands.Cog.listener()
    async def on_voice_state_update(self, ctx, before, after):
        if before.channel != after.channel:
            logch = self.bot.get_channel(LOG_ID)
            txtch = self.bot.get_channel(TEST_ID)
            # レギマ 806547374884651038 ロビー 805097517318537271
            vchannels = [806547374884651038, 805097517318537271]
            dt_now = dt.now(JST)

            # 退室通知
            if before.channel is not None and before.channel.id in vchannels:
                # 入室時のログを参照
                try:
                    conn = fnc.get_connection()
                    cur = conn.cursor()
                    sql = (
                        "SELECT id, entry_time, CURRENT_TIMESTAMP - entry_time as duration "
                        "FROM vc_logs WHERE user_id = %s AND ch_id = %s ORDER BY id DESC LIMIT 1;"
                    )
                    cur.execute(
                        sql,
                        (str(ctx.id), str(before.channel.id)),
                    )
                    vc_status = cur.fetchone()
                    cur.close()
                    # 退出時間を記録
                    cur = conn.cursor()
                    sql = "UPDATE vc_logs SET leaving_time = CURRENT_TIMESTAMP, duration = %s WHERE id = %s;"
                    cur.execute(
                        sql,
                        (vc_status[2], vc_status[0]),
                    )
                    conn.commit()
                    conn.close()
                except psycopg2.OperationalError as e:
                    await txtch.send("DBへの登録に失敗したよ！")
                    await txtch.send("ERROR:" + str(e))
                await logch.send(
                    "[VC] **"
                    + before.channel.name
                    + "** から、__"
                    + ctx.name
                    + "__  が退室しました！ ["
                    + dt_now.strftime("%Y/%m/%d %H:%M:%S")
                    + "]"
                )
            # 入室通知
            if after.channel is not None and after.channel.id in vchannels:
                try:
                    conn = fnc.get_connection()
                    cur = conn.cursor()
                    sql = "INSERT INTO vc_logs (user_id, ch_id, entry_time) VALUES (%s, %s, %s);"
                    cur.execute(
                        sql,
                        (
                            str(ctx.id),
                            str(after.channel.id),
                            dt_now.strftime("%Y/%m/%d %H:%M:%S"),
                        ),
                    )
                    conn.commit()
                    conn.close()
                except psycopg2.OperationalError as e:
                    await txtch.send("DBへの登録に失敗したよ！")
                    await txtch.send("ERROR:" + str(e))
                await logch.send(
                    "[VC] **"
                    + after.channel.name
                    + "** に、__"
                    + ctx.name
                    + "__  が入室しました！ ["
                    + dt_now.strftime("%Y/%m/%d %H:%M:%S")
                    + "]"
                )

    @commands.command()
    async def vcstatus(self, ctx):
        await ctx.send("ボイスチャット利用情報")
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
        # 使用時間を時分秒に変換する
        btl = ev.get_remain(vc_info[0][2])
        lb = ev.get_remain(vc_info[1][2])
        av_btl = ev.get_remain(vc_info[0][3])
        av_lb = ev.get_remain((vc_info[1][3]))
        await ctx.send(
            "外征/レギマ：{0}時間{1}分{2}秒 ({3}時間{4}分{5}秒/日)".format(
                btl[0], btl[1], btl[2], av_btl[0], av_btl[1], av_btl[2]
            )
        )
        await ctx.send(
            "ロビー：{0}時間{1}分{2}秒 ({3}時間{4}分{5}秒/日)".format(
                lb[0], lb[1], lb[2], av_lb[0], av_lb[1], av_lb[2]
            )
        )

    # @commands.command()
    # async def monthlog(self, ctx):
    #     sql = """
    #         SELECT
    #             ch_id
    #             , COUNT(*) AS 利用日数
    #             , SUM(日次合計) AS 月間使用時間
    #             , SUM(日次合計) / COUNT(*) AS 日平均利用時間
    #         FROM
    #             (
    #                 SELECT
    #                     ch_id
    #                     , TO_CHAR(entry_time, 'YYYY/MM/DD') AS 利用日
    #                     , MAX(duration) AS 日次合計
    #                 FROM
    #                     vc_logs
    #                 WHERE
    #                     DATE_PART('month', now()) - 1 = DATE_PART('month', entry_time)
    #                     AND EXTRACT(EPOCH FROM duration ::time) > 60
    #                 GROUP BY
    #                     ch_id
    #                     , 利用日
    #                 ORDER BY
    #                     利用日
    #             ) daily_logs
    #         GROUP BY
    #             ch_id
    #         ORDER BY
    #             ch_id DESC;
    #         """
    #     vc_month = fnc.select_sql_without_param_fetchall(sql)
    #     # 使用時間を時分秒に変換する
    #     btl = ev.get_remain(vc_month[0][2])
    #     lb = ev.get_remain(vc_month[1][2])
    #     av_btl = ev.get_remain(vc_month[0][3])
    #     av_lb = ev.get_remain((vc_month[1][3]))
    #     await ctx.send(
    #         "外征/レギマ：{0}時間{1}分{2}秒 ({3}時間{4}分{5}秒/日)".format(
    #             btl[0], btl[1], btl[2], av_btl[0], av_btl[1], av_btl[2]
    #         )
    #     )
    #     await ctx.send(
    #         "ロビー：{0}時間{1}分{2}秒 ({3}時間{4}分{5}秒/日)".format(
    #             lb[0], lb[1], lb[2], av_lb[0], av_lb[1], av_lb[2]
    #         )
    #     )
    #     print(vc_month[0][2])
    #     print(vc_month[1][2])
    #     conn = fnc.get_connection()
    #     for i in range(len(vc_month)):
    #         t = td(seconds=86400)
    #         # vc_month[i][2]が86400秒を超えた場合の処理
    #         # total_seconds()を文字列変換して●h●m●sの形にする?
    #         # もしくはSQLで加算処理する(こっちのほうがかんたんかも)
    #
    #         # if vc_month[i][2].total_seconds() >= t.total_seconds():
    #         #     vc_month[i][2] += t
    #         cur = conn.cursor()
    #         sql = (
    #             "INSERT INTO vc_monthly_logs (month, ch_id, monthly_use_time) "
    #             "VALUES ( TO_CHAR(CURRENT_DATE + CAST( '-7 days' AS INTERVAL ) , 'YYYY/MM'), %s, %s)"
    #         )
    #         cur.execute(sql, (str(vc_month[i][0]), vc_month[i][2]))
    #     conn.commit()
    #     conn.close()
    #     await ctx.send("月間データが登録されました")


def setup(bot):
    bot.add_cog(Vchat(bot))
