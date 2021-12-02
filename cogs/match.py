from discord.ext import commands
import discord
import functions as fnc
import psycopg2
import os
from cogs.help import get_help_match

# 本番用テキストチャンネル
CHANNEL_ID = int(os.environ["PERFORMANCE_CHANNEL"])
# ログ管理用クローズドチャンネル
TEST_ID = int(os.environ["TEST_CHANNEL"])
# 投稿権限を持つユーザー
SCORER_USER = int(os.environ["SCORER"])


class Match(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    # Cogが読み込まれた時に発動
    async def on_ready(self):
        print("Load Match module...")

    @commands.command()
    async def match(self, ctx, *args):
        channel = self.bot.get_channel(TEST_ID)
        if len(args) == 0 or args[0] == "":
            # レギオンリーグに対応
            sql = "SELECT DISTINCT result, COUNT(result) FROM match_records GROUP BY result ORDER BY result DESC;"
            # sql = "SELECT DISTINCT result, COUNT(result) FROM match_records2 GROUP BY result ORDER BY result DESC;"
            result = fnc.select_sql_without_param_fetchall(sql)
            if len(result) == 0:
                await ctx.send("戦績情報が登録されていないよ!")
                return
            elif len(result) == 1 and result[0][0] == 1:
                win = result[0][1]
                lose = 0
            elif len(result) == 1 and result[0][0] == -1:
                win = 0
                lose = result[0][1]
            else:
                win = result[0][1]
                lose = result[1][1]
            rate = round((win / (win + lose)) * 100, 2)
            # rate = win / (win + lose) * 100
            await ctx.send(
                "現在の戦績は" + str(win) + "勝" + str(lose) + "敗（勝率" + str(rate) + "％）だよ！"
            )
            return
        # 過去5戦分の戦績を表示
        # /match -h
        elif args[0] == "-h" and len(args) == 1:
            if not fnc.get_league_period():
                sql = "SELECT * FROM match_records ORDER BY id desc LIMIT 5;"
                results = fnc.select_sql_without_param_fetchall(sql)
            else:
                league_start = fnc.worksheet.acell("B12").value
                sql = "SELECT * FROM match_records2 WHERE created_at > %s ORDER BY id desc LIMIT 6;"
                results = fnc.select_sql_with_param_fetchall(sql, (league_start,))
            embed = discord.Embed(
                title="直近" + str(len(results)) + "戦の戦績", color=0xFFFFFF
            )
            for result in results:
                judge = fnc.judge_results(result)
                embed.add_field(
                    name=result[5].strftime("%m月%d日") + ":" + result[1],
                    value="<"
                    + judge
                    + "> "
                    + " ["
                    + "{:,}".format(int(result[2]))
                    + "]  VS  ["
                    + "{:,}".format(result[3])
                    + "]",
                    inline=False,
                )
            await ctx.send(embed=embed)
            return

        elif args[0] == "-help":
            embed = get_help_match()
            await ctx.send(embed=embed)
            return

        elif args[0] == "-h" and len(args[1]) != 0:
            # レギオン名で戦績の履歴を検索ができるようにする
            search = str(args[1])
            sql = "SELECT * FROM match_records WHERE legion_name LIKE %s\
                UNION SELECT * FROM match_records2 WHERE legion_name LIKE %s ORDER BY created_at DESC"
            results = fnc.select_sql_with_param_fetchall(
                sql, ("%" + str(search) + "%", "%" + str(search) + "%")
            )
            if len(results) != 0:
                sql = """
                        SELECT DISTINCT
                            result
                            , COUNT(result)
                        FROM
                            (
                                SELECT
                                    *
                                FROM
                                    match_records
                                WHERE
                                    legion_name = %s
                                UNION
                                SELECT
                                    *
                                FROM
                                    match_records2
                                WHERE
                                    legion_name = %s
                            ) match
                        GROUP BY
                            result
                        ORDER BY
                            result DESC
                      """
                # legion = "%" + results[0][1] + "%"
                legion = results[0][1]
                counts = fnc.select_sql_with_param_fetchall(sql, (legion, legion))
                win = 0
                lose = 0
                if len(counts) == 1:
                    if counts[0][0] == 1:
                        win = counts[0][1]
                    else:
                        lose = counts[0][1]
                elif len(counts) == 2:
                    win = counts[0][1]
                    lose = counts[1][1]
                if win > lose:
                    color = 0xFF0000
                elif win < lose:
                    color = 0x0000FF
                else:
                    color = 0xFFFFFF

                embed = discord.Embed(
                    title=str(results[0][1])
                    + "の対戦履歴 ("
                    + str(win)
                    + "勝"
                    + str(lose)
                    + "敗)",
                    color=color,
                )
                for result in results:
                    judge = fnc.judge_results(result)
                    embed.add_field(
                        name=result[5].strftime("%m月%d日"),
                        value="<"
                        + judge
                        + "> "
                        + " ["
                        + "{:,}".format(int(result[2]))
                        + "]  VS  ["
                        + "{:,}".format(result[3])
                        + "]",
                        inline=False,
                    )
                    embed.add_field(
                        name="対戦動画",
                        value=result[6],
                        inline=False,
                    )
                await ctx.send(embed=embed)
                return
            else:
                await ctx.send("該当するレギオンが見つからなかったよ！")
                return

        # 過去のレギオンリーグの成績を表示
        # /match -l int
        elif args[0] == "-l":
            if len(args) != 2:
                await ctx.send("必要な情報が不足しているよ")
                return
            if args[1].isdecimal():
                cnt = int(args[1]) - 1
            else:
                await ctx.send("正しい値を入力してね")
                return
            sql = "SELECT * FROM match_records2 ORDER BY created_at LIMIT 6 OFFSET %s * 5 + %s ;"
            results = fnc.select_sql_with_param_fetchall(
                sql,
                (
                    cnt,
                    cnt,
                ),
            )
            if results is None:
                await ctx.send("該当するリーグが見つからなかったよ！")

            embed = discord.Embed(
                title="第" + str(cnt + 1) + "回レギオンリーグの戦績", color=0xFFFFFF
            )
            for result in results:
                if result[4] == -1:
                    judge = "敗北"
                elif result[4] == 1:
                    judge = "勝利"
                else:
                    judge = "引分けかデータ不良"
                embed.add_field(
                    name=result[5].strftime("%m月%d日") + ":" + result[1],
                    value="<"
                    + judge
                    + "> "
                    + " ["
                    + "{:,}".format(int(result[2]))
                    + "]  VS  ["
                    + "{:,}".format(result[3])
                    + "]",
                    inline=False,
                )
            await ctx.send(embed=embed)
            return

        elif len(args) == 1:
            # TODO:過去の戦歴を検索
            search = str(args[0])
            sql = "SELECT * FROM match_records WHERE legion_name LIKE %s\
                UNION SELECT * FROM match_records2 WHERE legion_name LIKE %s ORDER BY created_at DESC"
            result = fnc.select_sql_with_param_fetch(
                sql, ("%" + str(search) + "%", "%" + str(search) + "%")
            )
            if result is None:
                await ctx.send("該当するレギオンが見つからなかったよ！")
                return
            if result[4] == -1:
                judge = "敗北"
                color = 0x0000FF
            elif result[4] == 1:
                judge = "勝利"
                color = 0xFF0000
            else:
                judge = "引分けかデータ不良"
                color = 0xFFFFFF
            embed = discord.Embed(
                title="前回の戦績", description="相手レギオン名：" + result[1], color=color
            )
            embed.add_field(name="結果", value=judge, inline=False)
            embed.add_field(
                name="前回対戦日", value=result[5].strftime("%Y年%m月%d日"), inline=False
            )
            embed.add_field(
                name="マッチpt",
                value=" ["
                + "{:,}".format(int(result[2]))
                + "]  VS  ["
                + "{:,}".format(result[3])
                + "]",
                inline=False,
            )
            embed.add_field(name="対戦動画", value=result[6], inline=False)
            await ctx.send(embed=embed)
            return
        if (
            not ctx.author.guild_permissions.administrator
            and ctx.author.id != SCORER_USER
        ):
            await ctx.send("投稿できる権限がありません!")
            return
        if len(args) < 3:
            await ctx.send("登録に必要な情報が不足しているよ！")
            return
        url = None
        if len(args) == 4:
            url = str(args[3])
        try:
            legion_name = str(args[0])
            my_score = int(args[1])
            nme_score = int(args[2])
        except ValueError as ve:
            await ctx.send("入力値が正しくないよ！")
            await channel.send("ERROR:" + str(ve))
            return

        if my_score > nme_score:
            result = (1, "勝利")
        elif my_score < nme_score:
            result = (-1, "敗北")
        else:
            result = (0, "引分け")

        l_sql = "SELECT * FROM legions ORDER BY created_at DESC LIMIT 1"
        legion = fnc.select_sql_without_param_fetch(l_sql)
        try:
            conn = fnc.get_connection()
            cur = conn.cursor()
            # レギオンリーグに対応
            if not fnc.get_league_period():
                sql = (
                    "INSERT INTO match_records (legion_name, my_score, nme_score, result, url, legion_id) "
                    "VALUES (%s, %s, %s, %s, %s, %s)"
                )
            else:
                sql = (
                    "INSERT INTO match_records2 (legion_name, my_score, nme_score, result, url, legion_id) "
                    "VALUES (%s, %s, %s, %s, %s, %s)"
                )
            cur.execute(
                sql, (legion_name, my_score, nme_score, result[0], url, legion[0])
            )
            conn.commit()
            conn.close()
        except psycopg2.OperationalError as e:
            await ctx.send("DBへの登録に失敗したよ！")
            await channel.send("ERROR:" + str(e))
            return
        if result[0] == 1:
            color = 0xFF0000
        else:
            color = 0x0000FF
        embed = discord.Embed(
            title="戦績を登録しました", description="相手レギオン名：" + legion_name, color=color
        )
        embed.add_field(name="結果", value=result[1], inline=False)
        embed.set_footer(
            text="マッチpt：姉妹関係推進課 ["
            + "{:,}".format(my_score)
            + "]  VS  "
            + legion_name
            + "\
        ["
            + "{:,}".format(nme_score)
            + "]"
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Match(bot))
