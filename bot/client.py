import discord
from libs.config import Config

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"Zalogowano bota: {bot.user}")


@bot.slash_command(name="hello", description="Say hello to bot")
async def hello(ctx):
    await ctx.respond("Hello")

bot.run(Config.DISCORD_TOKEN)
