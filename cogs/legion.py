import discord
from discord.ext import commands
import psycopg2
import psycopg2.extras
import functions as fnc
from cogs.help import get_help_matome


def update_legion(ss_dic):
    try:
        conn = fnc.get_connection()
        psycopg2.extras.register_hstore(conn)
        cur = conn.cursor()
        sql = "UPDATE legions SET info = %s WHERE legion_name = %s"
        cur.execute(sql, (ss_dic, ss_dic["legion"]))
        conn.commit()
        conn.close()
        comment = "レギオン情報を更新しました"
    except psycopg2.OperationalError as e:
        comment = "レギオン情報の更新に失敗しました"
        print("ERROR:" + e)
    return comment


def register_legion(ss_dic):
    sql = "SELECT COUNT(*) FROM legions;"
    con_legion = fnc.select_sql_without_param_fetch(sql)
    try:
        conn = fnc.get_connection()
        psycopg2.extras.register_hstore(conn)
        cur = conn.cursor()
        sql = "INSERT INTO legions (legion_id, legion_name, info, created_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)"
        cur.execute(sql, (con_legion[0] + 1, ss_dic["legion"], ss_dic))
        conn.commit()
        conn.close()
        comment = "レギオン情報を登録しました"
    except psycopg2.OperationalError as e:
        comment = "レギオン情報の登録に失敗しました"
        print("ERROR:" + e)
    return comment


# matchシート内の文字列を抽出して辞書を作成
def get_legion():
    ss_dic = {
        "date": fnc.worksheet2.acell("B3").value,
        "week": fnc.worksheet2.acell("C3").value,
        "legion": fnc.worksheet2.acell("B4").value,
        "title": fnc.worksheet2.acell("B5").value,
        "thumbnail": fnc.worksheet2.acell("B7").value,
        "description": fnc.worksheet2.acell("B6").value,
        "strategy": fnc.worksheet2.acell("B9").value,
        "v_formation": fnc.worksheet2.acell("B11").value,
        "r_formation": fnc.worksheet2.acell("B12").value,
        "order": fnc.worksheet2.acell("B19").value,
        "neun1": fnc.worksheet2.acell("B14").value,
        "neun2": fnc.worksheet2.acell("B15").value,
        "neun3": fnc.worksheet2.acell("B16").value,
        "neun_order": fnc.worksheet2.acell("A17").value,
        "lily1": fnc.worksheet2.acell("B22").value,
        "emoji1": fnc.worksheet2.acell("C22").value,
        "skill1": fnc.worksheet2.acell("D22").value,
        "timing1": fnc.worksheet2.acell("B24").value,
        "pl1": fnc.worksheet2.acell("E22").value,
        "lily2": fnc.worksheet2.acell("B23").value,
        "emoji2": fnc.worksheet2.acell("C23").value,
        "skill2": fnc.worksheet2.acell("D23").value,
        "timing2": fnc.worksheet2.acell("B25").value,
        "pl2": fnc.worksheet2.acell("E23").value,
        "priority": fnc.worksheet2.acell("B27").value,
        "atk1": fnc.worksheet2.acell("B29").value,
        "atk2": fnc.worksheet2.acell("C29").value,
        "atk3": fnc.worksheet2.acell("D29").value,
        "atk4": fnc.worksheet2.acell("E29").value,
        "sub_atk1": fnc.worksheet2.acell("B30").value,
        "sub_atk2": fnc.worksheet2.acell("C30").value,
        "sub_atk3": fnc.worksheet2.acell("D30").value,
        "sub_atk4": fnc.worksheet2.acell("E30").value,
        "multi1": fnc.worksheet2.acell("B31").value,
        "multi2": fnc.worksheet2.acell("C31").value,
        "multi3": fnc.worksheet2.acell("D31").value,
        "multi4": fnc.worksheet2.acell("E31").value,
        "sub_sp1": fnc.worksheet2.acell("B32").value,
        "sub_sp2": fnc.worksheet2.acell("C32").value,
        "sub_sp3": fnc.worksheet2.acell("D32").value,
        "sub_sp4": fnc.worksheet2.acell("E32").value,
        "sp1": fnc.worksheet2.acell("B33").value,
        "sp2": fnc.worksheet2.acell("C33").value,
        "sp3": fnc.worksheet2.acell("D33").value,
        "sp4": fnc.worksheet2.acell("E33").value,
        "memo": fnc.worksheet2.acell("A35").value,
    }
    for ss_key in ss_dic:
        ss_dic[ss_key] = ss_dic[ss_key] or ""
        if ss_dic[ss_key] is None:
            err = "入力値エラー"
            return err
    print("[notice] After Null check")
    return ss_dic


# レギオンテーブルのレコード存在確認
def exist_legion(ss_dic):
    sql = "SELECT COUNT(*) FROM legions WHERE legion_name = %s"
    count = fnc.select_sql_with_param_fetch(sql, (ss_dic["legion"],))
    if count[0] == 0:
        # INSERT
        comment = register_legion(ss_dic)
    else:
        # UPDATE
        comment = update_legion(ss_dic)
    return comment


def embed_legion(ss_dic):
    atks = f"{ss_dic['atk1']}　{ss_dic['atk2']}　{ss_dic['atk3']}　{ss_dic['atk4']}"
    if atks == "":
        atks = "なし"
    sub_atks = f"{ss_dic['sub_atk1']}　{ss_dic['sub_atk2']}　{ss_dic['sub_atk3']}　{ss_dic['sub_atk4']}"
    if sub_atks == "":
        sub_atks = "なし"
    multis = (
        f"{ss_dic['multi1']}　{ss_dic['multi2']}　{ss_dic['multi3']}　{ss_dic['multi4']}"
    )
    if multis == "":
        multis = "なし"
    spatks = f"{ss_dic['sp1']}　{ss_dic['sp2']}　{ss_dic['sp3']}　{ss_dic['sp4']}"
    if spatks == "":
        spatks = "なし"
    sub_spatks = f"{ss_dic['sub_sp1']}　{ss_dic['sub_sp2']}　{ss_dic['sub_sp3']}　{ss_dic['sub_sp4']}"
    if sub_spatks == "":
        sub_spatks = "なし"

    embed = discord.Embed(
        title=f"{ss_dic['legion']}　さん",
        description=ss_dic["description"],
        color=0xFFFFFF,
    )
    embed.set_author(name=f"{ss_dic['date']}({ss_dic['week']})　{ss_dic['title']}")
    embed.add_field(name="作戦方針", value=f"{ss_dic['strategy']}", inline=False)
    embed.add_field(
        name="編成方針",
        value=f"前衛:　{ss_dic['v_formation']} \n後衛:　{ss_dic['r_formation']}",
        inline=False,
    )
    embed.add_field(
        name="ノインヴェルト有効弾",
        value=f"{ss_dic['neun1']}　{ss_dic['neun2']}　{ss_dic['neun3']}",
        inline=False,
    )
    embed.add_field(
        name=f"レアスキル\n①{ss_dic['skill1']}　担当:　{ss_dic['pl1']}",
        value=f"リリィ:　{ss_dic['lily1']} {ss_dic['emoji1']}\nタイミング:　{ss_dic['timing1']}",
        inline=False,
    )
    embed.add_field(
        name=f"②{ss_dic['skill2']}　担当:　{ss_dic['pl2']}",
        value=f"リリィ:　{ss_dic['lily2']} {ss_dic['emoji2']}\nタイミング:　{ss_dic['timing2']}",
        inline=False,
    )
    embed.add_field(name="ノイン順番", value=ss_dic["neun_order"], inline=False)
    embed.add_field(name="オーダーTL", value=ss_dic["order"], inline=False)
    embed.add_field(name="相手編成まとめ", value=f"優先:　{ss_dic['priority']}", inline=False)
    embed.add_field(name="物理特化", value=atks, inline=True)
    embed.add_field(name="物理寄り", value=sub_atks, inline=True)
    embed.add_field(name="マルチ", value=multis, inline=False)
    embed.add_field(name="特殊特化", value=spatks, inline=True)
    embed.add_field(name="特殊寄り", value=sub_spatks, inline=True)
    return embed


class Legion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    # Cogが読み込まれた時に発動
    async def on_ready(self):
        print("Load Legion module...")

    @commands.command()
    async def matome(self, ctx, *args):
        try:
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("コマンドの実行権限がないよ!")
                return
        except AttributeError as ae:
            await ctx.send("そのコマンドはここでは実行できないよ!")
            print(ae)
            return

        # matchシート内の文字列を抽出して辞書を作成
        ss_dic = get_legion()
        # レギオン情報登録処理
        # レギオンテーブルのレコード存在確認
        comment = exist_legion(ss_dic)
        if len(args) != 0 and args[0] == "-r":
            await ctx.send(comment)
            return
        elif len(args) != 0 and args[0] == "-help":
            embed = get_help_matome()
            await ctx.send(embed=embed)
            return
        embed = embed_legion(ss_dic)
        await ctx.send("@everyone\n今日の対戦相手と作戦を確認しようね！")
        await ctx.send(embed=embed)
        await ctx.send(comment)
        fnc.worksheet2.update_acell("F6", "OK")


def setup(bot):
    bot.add_cog(Legion(bot))
