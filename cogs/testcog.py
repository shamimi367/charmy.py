from discord.ext import commands
from datetime import datetime as dt, timedelta as td, timezone as tz
import cogs.event as ev


class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    # Cogが読み込まれた時に発動
    async def on_ready(self):
        print("Cog Test Code")

    @commands.command()
    async def gets_events(self, ctx):
        dt_now = dt.now(JST)
        current_event = ev.get_event_data()
        print(current_event)
        events = ev.get_all_events()
        print(events)
        print(current_event is not None)
        if current_event is not None:
            dt_event = current_event[1]
            print(dt_now.date() == dt_event.date())


def setup(bot):
    bot.add_cog(TestCog(bot))
