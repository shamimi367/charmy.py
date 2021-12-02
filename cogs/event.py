from discord.ext import commands
from datetime import datetime as dt, timedelta as td, timezone as tz

# ワークシートをインポート
from functions import worksheet

# イベント開催情報
event1_name = event1_date = event1_medal = ""
event2_name = event2_date = event2_medal = ""
gacha1_name = gacha1_expiry = gacha2_name = gacha2_expiry = ""
# タイムゾーンの生成
JST = tz(td(hours=+9), "JST")


# スプレッドシートにイベント情報を登録
def set_event_data():
    # イベント開催情報
    global event1_name, event1_date, event1_medal, event2_name, event2_date, event2_medal
    event1_name = worksheet.acell("B2").value
    event1_date = dt.strptime(worksheet.acell("B3").value, "%Y-%m-%d %H:%M:%S")
    event1_medal = dt.strptime(worksheet.acell("B4").value, "%Y-%m-%d %H:%M:%S")
    event2_name = worksheet.acell("D2").value
    event2_date = dt.strptime(worksheet.acell("D3").value, "%Y-%m-%d %H:%M:%S")
    event2_medal = dt.strptime(worksheet.acell("D4").value, "%Y-%m-%d %H:%M:%S")
    return None


# スプレッドシートのガチャ情報を登録
def set_gacha_data():
    global gacha1_name, gacha1_expiry, gacha2_name, gacha2_expiry
    # ガチャメダル引き換え期限
    gacha1_name = worksheet.acell("B6").value
    gacha1_expiry = dt.strptime(worksheet.acell("B7").value, "%Y-%m-%d %H:%M:%S")
    gacha2_name = worksheet.acell("D6").value
    gacha2_expiry = dt.strptime(worksheet.acell("D7").value, "%Y-%m-%d %H:%M:%S")


def get_gacha_data():
    set_gacha_data()
    return gacha1_name, gacha1_expiry, gacha2_name, gacha2_expiry


def get_all_events():
    set_event_data()
    return (
        event1_name,
        event1_date,
        event1_medal,
        event2_name,
        event2_date,
        event2_medal,
    )


# スプレッドシートから現在開催中のイベント情報を取得
# return tuple ('event_name', 'event_date', 'event_medal')
def get_event_data():
    dt_now = dt.now() + td(hours=+0)
    if dt_now <= event1_date:
        if dt_now <= event2_date:
            if event1_date < event2_date:
                return event1_name, event1_date, event1_medal
            else:
                return event2_name, event2_date, event2_medal
        else:
            return event1_name, event1_date, event1_medal
    elif dt_now <= event2_date:
        return event2_name, event2_date, event2_medal


def get_remain(td):
    m, s = divmod(td.total_seconds(), 60)
    h, m = divmod(m, 60)
    return str(round(h)), str(round(m)), str(round(s))


class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    # Cogが読み込まれた時に発動
    async def on_ready(self):
        print("Load Event module...")

    @commands.command()
    async def event(self, ctx, *args):
        set_event_data()
        event_data = get_event_data()
        if event_data is None:
            set_event_data()
            await ctx.send("イベントが開催されていないか、イベントデータが正常に取得できてないよ!")
            return
        dted = event_data[1]
        stred = dt.strftime(dted, "%Y年%m月%d日 %H時%M分")
        now = dt.now() + td(hours=+0)
        remain = dted - now

        if remain.days > 0:
            await ctx.send(
                "開催中のイベント『"
                + event_data[0]
                + "』は\n"
                + stred
                + "までだよ! (残り"
                + str(remain.days)
                + "日)"
            )
        elif now < dted:
            ir = get_remain(remain)
            await ctx.send(
                "開催中のイベント『"
                + event_data[0]
                + "』は\n"
                + stred
                + "までだよ! (残り"
                + ir[0]
                + "時間"
                + ir[1]
                + "分)"
            )
        else:
            await ctx.send("イベント『" + event_data[0] + "』は開催期間が終了したよ!おつかれさま!")

    @commands.command()
    async def get_events(self, ctx):
        set_event_data()
        set_gacha_data()
        get_event_data()
        print(get_all_events())
        print(type(get_all_events()))
        print(get_gacha_data())
        print(type(get_gacha_data()))


def setup(bot):
    bot.add_cog(Event(bot))
