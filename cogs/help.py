from discord.ext import commands
import discord


# 各コマンドの詳細を呼び出す

# /rem
def get_help_reminder():
    embed = discord.Embed(
        title="リマインダー機能",
        description="メモリアメダルや物資庫の鍵の使用期限やさまざまなスケジュールの管理が出来ます。\n"
        "リマインド設定日当日の午前9時にチャーミィがDMで予定をお知らせします。",
        color=0xFFFFFF,
    )
    embed.add_field(
        name="リマインダー登録：/rem + [登録したい項目] + [(yyyy/)mm/dd] +  [mm:ss]",
        value="例) /rem 叶星さま誕生日 2021/10/31 00:00(西暦を省略すると今年になります)\n"
        "の形式で入力すると、リマインダーが新規に登録されます。",
        inline=False,
    )
    embed.add_field(
        name="リマインダーの一覧表示：/rem",
        value="自身の登録済みのリマインダーの一覧が表示されます、自分以外のリマインダーは表示されません。\n"
        "リマインダーを削除したい時には先頭のリマインダーIDを使用してください。",
        inline=False,
    )
    embed.add_field(
        name="リマインダー削除：/drem + [削除したいリマインダーのID]",
        value="例) /drem 3429\n"
        "自身の登録済のリマインダーを削除することができます。\n"
        "自分以外のリマインダーを削除することはできません。",
        inline=False,
    )
    return embed


# /skill
def get_help_skill():
    embed = discord.Embed(
        title="レアスキル検索機能",
        description="レアスキル名称の一部を入力すると該当レアスキルの情報を表示します。",
        color=0xFFFFFF,
    )
    embed.add_field(
        name="レアスキル検索: /skill + [調べたいレアスキル名(部分一致)]",
        value="例) /skill フェイズ(フェイストランセンデンスの結果を表示)\n"
        "ゲーム内におけるレアスキルの効果とレアスキル保持リリィを表示します。",
        inline=False,
    )
    return embed


# /birth
def get_help_birth():
    embed = discord.Embed(
        title="誕生日検索機能",
        description="ゲーム内プレイアブルキャラとして実装済みリリィの誕生日を検索できます。",
        color=0xFFFFFF,
    )
    embed.add_field(
        name="直近誕生日のリリィを検索： /birth",
        value="一番直近に誕生日を迎えるリリィ名と誕生日を表示します。",
        inline=False,
    )
    embed.add_field(
        name="リリィの誕生日を検索： /birth + [リリィ名の一部(漢字 or ひらがな)]",
        value="例) /birth くれは\n"
        "この場合、土岐紅巴の誕生日を表示します。\n"
        "名前にカタカナを含むリリィのみカタカナでの検索にも対応します",
        inline=False,
    )
    embed.add_field(
        name="自動投稿",
        value="午前9時に当日誕生日を迎えるリリィの名前を自動で投稿します",
        inline=False,
    )
    return embed


# /middle
def get_help_middle():
    embed = discord.Embed(
        title="まんなかバースデー検索機能", description="任意のリリィ2人のまんなかバースデーを検索します", color=0xFFFFFF
    )
    embed.add_field(
        name="/middle + [任意の2人のカプ名(読み)]",
        value="例) /middle たかなほ\n"
        "入力された5文字以下の文字列からカップリングを推測し、カプ名に該当すれば2人のまんなかバースデーを表示します\n"
        "リバ検索や3文字を含むカプ名にも対応(しぇんゆー、ゆーしぇん)、ただし漢字の検索には非対応です。",
        inline=False,
    )
    return embed


# /match
def get_help_match():
    embed = discord.Embed(
        title="戦績表示機能", description="レギオンマッチ、レギオンリーグに関する情報を表示、検索します", color=0xFFFFFF
    )
    embed.add_field(
        name="レギマ戦績表示: /match",
        value="レギマの通算戦績と勝率を表示します。戦績はゲーム内レギオンページの情報に準じます。",
        inline=False,
    )
    embed.add_field(
        name="相手レギオンとの対戦履歴を表示: /match + [相手レギオン名(部分一致)]",
        value="検索結果に該当するレギオンとの対戦結果、スコア、リプレイを表示します。",
        inline=False,
    )
    embed.add_field(
        name="過去5戦分のレギマ、レギリの対戦履歴を表示: /match -h",
        value="最新の最大5件分のレギマの対戦結果、スコア履歴を表示します。\n"
        "レギリ期間中なら当該期間中のレギリから、開催期間外であればレギマから抽出します。",
        inline=False,
    )
    embed.add_field(
        name="相手レギオンとの対戦履歴を表示: /match -h + [相手レギオン名(部分一致)]",
        value="検索結果に該当するレギオンとの対戦結果、スコア、リプレイの履歴を表示します。",
        inline=False,
    )
    embed.add_field(
        name="レギリの戦績を表示: /match -l + [数字]",
        value="第[数字]回レギリの対戦結果、スコアの履歴を表示します。",
        inline=False,
    )
    embed.add_field(
        name="対戦結果を登録: /match [レギオン名] + [自軍スコア] + [相手スコア] + [動画URL]",
        value="レギリ期間中であればレギリDBに、それ以外であればレギマDBに対戦結果を登録します(権限者のみ)",
        inline=False,
    )
    return embed


# /matome
def get_help_matome():
    embed = discord.Embed(
        title="作戦情報まとめ機能(管理者のみ)",
        description="作戦まとめチャンネルにレギマ、レギリ当日の作戦情報を投稿します。",
        color=0xFFFFFF,
    )
    embed.add_field(
        name="まとめを投稿: /matome",
        value="予め記入した作戦をまとめた情報をまとめチャンネルに投稿し、レギオンDBに登録します。",
        inline=False,
    )
    embed.add_field(
        name="レギオン情報を登録、更新: /matome -r",
        value="チャンネルには記事を投稿せずにレギオンDBの情報を登録、更新します。",
        inline=False,
    )
    return embed


# /event
def get_help_event():
    embed = discord.Embed(
        title="イベント情報", description="現在開催中のゲーム内イベントに関する情報を表示します。", color=0xFFFFFF
    )
    embed.add_field(
        name="/event",
        value="現在開催中のイベント情報や残りの開催期間の情報を表示します。",
        inline=False,
    )
    return embed


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    # Cogが読み込まれた時に発動
    async def on_ready(self):
        print("Load Help Command...")

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="チャーミィができること",
            description="以下のコマンド(先頭に/から始まる命令もしくは直接リプライ)をサーバ内の\n"
            "テキストチャンネルかチャーミィとのDMで入力すると、下記の情報を返してくれます\n"
            "各コマンドに -help を付けると、コマンドごとの更に詳細な説明が表示されます",
            color=0xB3FF00,
        )
        embed.add_field(
            name="リマインダー機能: /rem /drem ",
            value="リマインダーを呼び出します。リマインダーの登録と削除、登録済みの自分のリマインダーを表示出来ます",
            inline=False,
        )
        embed.add_field(
            name="レアスキル検索機能: /skill",
            value="ゲーム内に実装済みのスキルの効果、対象リリィなどを検索することが出来ます",
            inline=False,
        )
        embed.add_field(
            name="誕生日検索機能: /birth /middle",
            value="実装済みリリィの誕生日に関する情報を検索することが出来ます。",
            inline=False,
        )
        embed.add_field(
            name="レギオンマッチ関連検索機能: /match",
            value="レギオンマッチの戦績など表示、検索します。レギオンリーグにも対応",
            inline=False,
        )
        embed.add_field(
            name="作戦情報まとめ機能: /matome",
            value="レギマ前の作戦投稿に使用します。管理者権限のある人のみ使用できます",
            inline=False,
        )
        embed.add_field(
            name="イベント関連機能: /event",
            value="現在開催中のゲーム内イベントに関する情報を表示します。",
            inline=False,
        )
        embed.add_field(
            name="ボイスチャット使用時間: /vcstatus",
            value="今月の外征ch、雑談chの利用時間(概算)を表示します。",
            inline=False,
        )
        embed.add_field(
            name="/help",
            value="このコマンドです。機能追加があれば随時更新します(隠しコマンドがあるとかないとか)",
            inline=False,
        )
        embed.add_field(
            name="自動投稿",
            value="レギマ、レギリ開催日の朝/レギマ・外征1時間前/レギマ前に作戦情報を投稿\n"
            "イベント最終日とメンテ日の昼、各種コインの交換期限日に注意を促すメッセージを自動投稿します。",
            inline=True,
        )
        embed.set_footer(text="運用：レギオン姉妹関係推進課 お茶汲み係")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
