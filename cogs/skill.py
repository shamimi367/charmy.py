from discord.ext import commands
import discord
import functions as fnc
from cogs.help import get_help_skill


class Skill(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    # Cogが読み込まれた時に発動
    async def on_ready(self):
        print("Load Skill module...")

    @commands.command()
    async def skill(self, ctx, *args):
        if len(args) == 0 or args[0] == "":
            await ctx.send("調べたいレアスキルの名前を入力してね!")
            return
        search = args[0]
        if args[0] == "-help":
            embed = get_help_skill()
            await ctx.send(embed=embed)
            return
        sql = "SELECT name, skill, effect FROM characters\
               LEFT OUTER JOIN skills\
               ON characters.skill_cd = skills.id\
               WHERE skill_cd = (SELECT id FROM skills WHERE skill LIKE %s);"
        result = fnc.select_sql_with_param_fetch(sql, ("%" + str(search) + "%",))
        if result is None:
            await ctx.send("そのレアスキルはまだ未実装か、名前が間違ってるよ!")
            return
        results = fnc.select_sql_with_param_fetchall(sql, ("%" + str(search) + "%",))
        members = ""
        for i in range(len(results)):
            members += results[i][0] + " / "
        embed = discord.Embed(
            title=results[0][1], description=results[0][2], color=0x7289DA
        )
        embed.set_footer(text="スキル保有者： " + members)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Skill(bot))
