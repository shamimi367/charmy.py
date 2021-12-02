from discord.ext import commands
import os
from datetime import datetime as dt, timedelta as td, timezone as tz
import functions as fnc
from cogs.help import get_help_birth
from cogs.help import get_help_middle

# 本番用テキストチャンネル
CHANNEL_ID = int(os.environ["PERFORMANCE_CHANNEL"])
# ログ管理用クローズドチャンネル
TEST_ID = int(os.environ["TEST_CHANNEL"])
# タイムゾーンの生成
JST = tz(td(hours=+9), "JST")


# 4文字なら前から2文字目で、5文字なら前から3文字目で分割する
def get_couple_name(search):
    if len(search) == 4:
        s1 = search[0:2]
        s2 = search[2:4]
        return s1, s2
    elif len(search) == 5:
        s1 = search[0:3]
        s2 = search[3:5]
        s3 = search[0:2]
        s4 = search[2:5]
        return s1, s2, s3, s4
    else:
        return None


def get_to_birth(b1, b2):
    nyd = dt(2021, 1, 1)
    # 1月1日からの経過日数を加算
    tb1 = b1 - nyd.date()
    tb2 = b2 - nyd.date()
    sum_birth = tb1 + tb2
    if sum_birth.days % 2 == 0:  # 割り切れたら
        half = sum_birth.days / 2
        half_bd = nyd + td(days=int(half))
        return half_bd
    else:
        hf = (sum_birth.days + 1) / 2
        half_bd1 = nyd + td(days=int(hf))
        if tb1.days < tb2.days:
            add_tb1 = tb1.days + 365
            half = (add_tb1 + tb2.days) / 2
            half_bd2 = nyd + td(days=int(half))
            return half_bd1, half_bd2
        else:
            add_tb2 = tb2.days + 365
            half = (tb1.days + add_tb2) / 2
            half_bd2 = nyd + td(days=int(half))
            return half_bd1, half_bd2


class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    # Cogが読み込まれた時に発動
    async def on_ready(self):
        print("Load Birthday module...")

    @commands.command()
    async def birth(self, ctx, *args):
        if len(args) == 0 or args[0] == "":
            dt_now = dt.now(JST)
            dtday = dt_now.date()
            sql = "SELECT name, birth_day FROM characters WHERE %s <= birth_day ORDER BY birth_day LIMIT 1;"
            result = fnc.select_sql_with_param_fetch(sql, (dtday,))
            birth_day = result[1].strftime("%-m月%-d日")
            if dtday == result[1]:
                await ctx.send(
                    "今日" + birth_day + "は" + result[0] + "さまの誕生日だよ!みんなでお祝いしようね!"
                )
                return
            else:
                await ctx.send(
                    "次に誕生日のお姉さまは"
                    + result[0]
                    + "さまで、誕生日は"
                    + birth_day
                    + "だよ!お祝いの準備をしようね!"
                )
                return
        search = args[0]
        if search == "-help":
            embed = get_help_birth()
            await ctx.send(embed=embed)
            return
        if "様" in search or "さま" in search:
            search = search.replace("さま", "").replace("様", "")
        if "ひめひめ" in search:
            search = search.replace("ひめひめ", "ひめか")
        sql = (
            "SELECT name, birth_day FROM characters WHERE name LIKE %s OR kana LIKE %s;"
        )
        result = fnc.select_sql_with_param_fetch(
            sql, ("%" + str(search) + "%", "%" + str(search) + "%")
        )
        if result is None:
            await ctx.send("そのお姉さまはまだ実装されていないみたいだよ!入力内容を確認してね!")
            return
        birth_day = result[1].strftime("%-m月%-d日")
        await ctx.send(result[0] + "さまのお誕生日は" + birth_day + "だよ!")

    @commands.command()
    async def middle(self, ctx, *args):
        if len(args) == 0 or args[0] == "":
            # argsが無かった場合の処理
            await ctx.send("別の名前で検索してみてね")
            return
        search = args[0]
        if search == "-help":
            embed = get_help_middle()
            await ctx.send(embed=embed)
            return
        cp = get_couple_name(search)
        # カプ名が見つからなかった時の処理
        if cp is None:
            await ctx.send("当てはまるカップルネームがなかったよ!別の名前で試してみてね!")
            return

        sql = "SELECT name, birth_day FROM characters WHERE name LIKE %s OR kana LIKE %s OR\
                name LIKE %s OR kana LIKE %s LIMIT 2;"
        param = (
            "%" + str(cp[0]) + "%",
            "%" + str(cp[0]) + "%",
            "%" + str(cp[1]) + "%",
            "%" + str(cp[1]) + "%",
        )
        result = fnc.select_sql_with_param_fetchall(sql, param)
        if len(search) == 5:
            if len(result) != 2:
                conn = fnc.get_connection()
                cur = conn.cursor()
                cur.execute(
                    sql,
                    (
                        "%" + str(cp[2]) + "%",
                        "%" + str(cp[2]) + "%",
                        "%" + str(cp[3]) + "%",
                        "%" + str(cp[3]) + "%",
                    ),
                )
                result = cur.fetchall()
                cur.close()
                conn.close()
        if len(result) != 2:
            await ctx.send("当てはまるカップルネームがなかったよ!別の名前で試してみてね!")
            return
        bd1 = result[0][1]
        bd2 = result[1][1]
        middle_bd = get_to_birth(bd1, bd2)
        md = "%m月%d日"
        if type(middle_bd) is tuple:
            middle_bd = f"{middle_bd[0].strftime(md)} (もしくは{middle_bd[1].strftime(md)})"
        else:
            middle_bd = middle_bd.strftime(md)
        await ctx.send(
            "["
            + search
            + "] "
            + result[0][0]
            + "さまと"
            + result[1][0]
            + "さまの\nまんなかバースデーは"
            + middle_bd
            + "だよ!"
        )


def setup(bot):
    bot.add_cog(Birthday(bot))
