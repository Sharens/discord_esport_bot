import discord
from libs.config import Config
from libs.prompt_template import active_games_template
from libs.pandascore.pandascore_libs import get_active_match_dict
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"Zalogowano bota: {bot.user}")


@bot.slash_command(
        name="active_games",
        description="Shows available games for Counter Strike 2"
)
async def active_games(ctx):
    await ctx.defer()
    await ctx.followup.send("Fetching active games...")

    active_games = get_active_match_dict()
    model = OllamaLLM(model="llama3.1")
    active_games_prompt = ChatPromptTemplate.from_template(
        active_games_template
    )
    chain = active_games_prompt | model
    response = chain.invoke({"games_dict": active_games})

    await ctx.respond(response)

bot.run(Config.DISCORD_TOKEN)
