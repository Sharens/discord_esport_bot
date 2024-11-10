import discord
from libs.config import Config


bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"Zalogowano bota: {bot.user}")


@bot.slash_command(guild_ids=Config.TEST_SERVER_ID)
async def hello(ctx):
    await ctx.respond("Hello")

bot.run(Config.DISCORD_TOKEN)