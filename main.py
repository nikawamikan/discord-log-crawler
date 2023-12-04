import discord
from discord.ext import commands
import os
import asyncio


intents = discord.Intents.default()
intents.guilds = True
bot = commands.AutoShardedBot(intents=intents)
TOKEN = os.getenv(f"TOKEN")

path = "./cogs"


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.respond(content="BOT管理者限定コマンドです", ephemeral=True)
    else:
        raise error


@bot.event
async def on_ready():
    print(f"Bot名:{bot.user} On ready!!")


bot.load_extensions(
    'cogs.hoge',
    store=False
)

bot.run(TOKEN)
