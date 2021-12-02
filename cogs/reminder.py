from discord.ext import commands
import discord
import psycopg2
import os
from datetime import datetime as dt, timedelta as td, timezone as tz
import functions as fnc
from cogs.help import get_help_reminder

# 本番用テキストチャンネル
CHANNEL_ID = int(os.environ["PERFORMANCE_CHANNEL"])
# ログ管理用クローズドチャンネル
TEST_ID = int(os.environ["TEST_CHANNEL"])
# タイムゾーンの生成
JST = tz(td(hours=+9), "JST")


class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Load Reminder module...")

    # args[0] 20xx/xx/xx xx:xx
    # args[1] 摘要
    @commands.command()
    async def rem(self, ctx, *args):
        # 任意のユーザーが任意のリマインダーメモを残せるようにする
        channel = self.bot.get_channel(TEST_ID)
        # 入力者のユーザーIDを取得
        author = ctx.author.id

        # 入力値を検査
        if len(args) == 0:
            # 引数がなかったときは登録メモしているメモを表示
            sql = "SELECT * FROM reminders WHERE player = %s ORDER BY end_time;"
            results = fnc.select_sql_with_param_fetchall(sql, (author,))
            if len(results) == 0:
                # リマインダーの登録がなければ
                await ctx.send("リマインダーが登録されてないよ!")
                return
            elif results[0] is None:
                await ctx.send("入力項目が不足しているよ！メモと月日は必ず登録してね！")
            else:
                reply = f"{ctx.author.mention}\n"
                embed = discord.Embed(
                    title="リマインダー",
                    description="登録件数" + str(len(results)) + "件",
                    color=0xFF8B33,
                )
                dt_now = dt.now() + td(hours=+0)
                for result in results:
                    if dt_now > result[3]:
                        embed.add_field(
                            name="~~[" + str(result[0]) + "]" + result[2] + "~~",
                            value="~~" + result[3].strftime("%Y/%m/%d %H:%M") + "~~",
                            inline=False,
                        )
                    else:
                        embed.add_field(
                            name="[" + str(result[0]) + "]" + result[2],
                            value=result[3].strftime("%Y/%m/%d %H:%M"),
                            inline=False,
                        )
                embed.set_footer(text="リマインダーを削除するには コマンド /drem xxxxx(ID番号) を実行してね！")
                await ctx.send(reply + "今はこれが登録されているよ！\n")
                await ctx.send(embed=embed)
        elif len(args) != 0 and args[0] == "-help":
            embed = get_help_reminder()
            await ctx.send(embed=embed)
            return
        else:
            # DBに入力値を登録
            # args[1]に西暦が含まれていない場合先頭に西暦を付加する
            end_time = str(args[1])
            if len(args[1]) <= 5:
                end_time = "2021/" + end_time
            if len(args) == 2:
                end = end_time
            elif len(args) == 3:
                end = end_time + " " + str(args[2])
            else:
                await ctx.send("入力値を確認してね!")
            try:
                conn = fnc.get_connection()
                cur = conn.cursor()
                sql = "INSERT INTO reminders (player, memo, end_time) VALUES (%s, %s, %s);"
                cur.execute(sql, (author, args[0], end))
                conn.commit()
                conn.close()
            except psycopg2.OperationalError as e:
                await ctx.send("DBへの登録に失敗したよ！")
                await channel.send("ERROR:" + str(e))
                return
            # 成功コメント
            await ctx.send("リマインダーを登録したよ!")
            await channel.send("新規のリマインダーが1件登録されました")

    @commands.command()
    async def drem(self, ctx, *args):
        # 登録したリマインダーを削除する
        channel = self.bot.get_channel(TEST_ID)
        # 入力値を検査する
        if len(args) == 0:
            await ctx.send("削除したいリマインダーのIDを教えてね!")
            return
        if not args[0].isdecimal():
            await ctx.send("正しい値を入力してね!")
        rem_id = int(args[0])
        author = ctx.author.id
        sql = "SELECT * FROM reminders WHERE id = %s;"
        result = fnc.select_sql_with_param_fetch(sql, (rem_id,))
        if result is None:
            await ctx.send("リマインダーIDを確認してね!")
            return
        if len(result) == 0:
            await ctx.send("リマインダーIDを確認してね!")
            return
        if author != result[1]:
            await ctx.send("そのリマインダーは削除できないよ!")
            return
        try:
            conn = fnc.get_connection()
            cur = conn.cursor()
            sql = "DELETE FROM reminders WHERE id = %s;"
            cur.execute(sql, (result[0],))
            conn.commit()
            conn.close()
        except psycopg2.OperationalError as e:
            await ctx.send("DBへの登録に失敗したよ！")
            await channel.send("ERROR:" + str(e))
            return
        await ctx.send("ID[" + str(result[0]) + "]のリマインダーを削除したよ!")
        await channel.send("1件のリマインダーが削除されました")


def setup(bot):
    bot.add_cog(Reminder(bot))
