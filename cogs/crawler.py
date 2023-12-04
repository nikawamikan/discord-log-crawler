import discord
from discord.ext import commands
from discord.commands import Option, OptionChoice, SlashCommandGroup
import json

# クローラーを実行する関数
async def crawler(ctx: discord.ApplicationContext, channel: discord.TextChannel, is_reverse: bool = True):
    channels = []
    messages = []
    count = 1
    # サーバー内のチャンネル一覧のidと名前を表示
    for channel in ctx.guild.channels:
        channels.append({"id": channel.id, "name": channel.name})      
        
    # メッセージのアーカイブを作成
    async for message in channel.history(limit=None):
        if count % 1000 == 0:
            await ctx.send(f"進捗: {channel.name} -> {count}")
        messages.append(
            {
                "channel_id": message.channel.id,
                "author_id": message.author.id,
                "author": message.author.name,
                "content": message.content,
                "created_at": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        count += 1
    
    # channels.jsonを作成
    with open(f"history/_channels.json", "w") as f:
        json.dump(channels, f, indent=4, ensure_ascii=False)

    # messagesの順番を逆転させる
    if is_reverse:
        messages.reverse()
    with open(f"history/{channel.name}-{channel.id}.json", "w") as f:
        json.dump(messages, f, indent=4, ensure_ascii=False)
    await ctx.send(f"{channel.name}のメッセージを保存しました -> {count-1} messages")


class Crawler(commands.Cog):

    def __init__(self, bot: commands.bot):
        print(f"init -> {self.__class__}")
        self.bot = bot

    group = SlashCommandGroup(name="crawler", description="クローラー関連のコマンド")

    @group.command(name="all_channel", description="すべてのテキストチャンネルのチャット履歴を保存します")
    async def all_channel(
        self,
        ctx: discord.ApplicationContext,
        is_reverse: Option(
            bool,
            description="メッセージの順番を降順にするかどうかを指定してください",
            default=True,
        ),
    ):
        await ctx.response.send_message(content="クロール対象のチャネル一覧を表示します")
        channels = await ctx.guild.fetch_channels()

        # textチャネルのみを抽出
        channels = [channel for channel in channels if isinstance(
            channel, discord.TextChannel)]

        # チャネル名を表示
        channel_names = [channel.name for channel in channels]
        await ctx.send(content="\n".join(channel_names))

        # チャネルごとの過去のメッセージをファイルに保存
        for channel in channels:
            await ctx.send(f"{channel.name}のメッセージを保存します")
            await crawler(ctx, channel, is_reverse)
        await ctx.send(content="クロールを終了します")

    @group.command(name="channel", description="指定したチャンネルのチャット履歴を保存します")
    async def channel(
        self,
        ctx: discord.ApplicationContext,
        is_reverse: Option(
            bool,
            description="メッセージの順番を降順にするかどうかを指定してください",
            default=True,
        ),
        channel: Option(
            discord.TextChannel,
            description="クロールを実行するチャンネルを指定してください",
            required=False,
        ),
    ):
        if channel is None:
            channel = ctx.channel
        await ctx.response.send_message(content="クロールを実行します")
        await crawler(ctx, channel, is_reverse)
        await ctx.send(content="クロールを終了します")


def setup(bot: commands.bot):
    bot.add_cog(Crawler(bot))
