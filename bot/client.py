import discord
import datetime
from libs.pandascore.pandascore_libs import (
    get_active_match_dict,
    get_tournament_details,
    add_player_to_tournament,
    get_tournament_roster
)

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"Zalogowano bota: {bot.user}")


@bot.slash_command(
        name="active_games",
        description="Pokazuje dostępne gry CS2"
)
async def active_games(ctx):
    await ctx.defer()
    try:
        active_games = get_active_match_dict()

        if not active_games:
            await ctx.respond("Brak aktywnych meczy w tym momencie.")
            return

        response = "**Aktualne rozgrywki e-sportowe z Counter Strike 2:**\n\n"

        for match_id, match_data in active_games.items():
            match_name, status, begin_at, teams, tournament_info = match_data

            # Formatowanie daty i godziny
            date_str = begin_at.strftime("%d.%m.%Y %H:%M") if begin_at else "TBA"

            # Dodawanie podstawowych informacji o meczu
            response += f"**({match_id}) {match_name}** | {date_str}\n"

            # Dodawanie informacji o turnieju, jeśli dostępne
            if tournament_info:
                response += f"🏆 Turniej: {tournament_info['name']}\n"

            # Dodawanie informacji o drużynach
            if teams:
                for team in teams:
                    response += f"    {team['name']}"
                    if team.get('acronym'):
                        response += f" [{team['acronym']}]"
                    response += "\n"
            else:
                response += "    Drużyny: TBA (To Be Announced)\n"

            response += "\n"

        await ctx.respond(response)

    except Exception as e:
        print(f"Szczegóły błędu: {str(e)}")
        await ctx.respond(f"Wystąpił błąd podczas pobierania danych: {str(e)}")


@bot.slash_command(
    name="tournament_details",
    description="Pokazuje szczegóły turnieju (podaj ID meczu lub turnieju)"
)
async def tournament_details(ctx, match_or_tournament_id: str):
    await ctx.defer()
    result = get_tournament_details(match_or_tournament_id)

    if result["success"]:
        tournament_data = result["data"]

        # Tworzymy czytelną odpowiedź
        response = "**🏆 Szczegóły Turnieju**\n\n"
        response += f"**Nazwa:** {tournament_data.get('name', 'Brak')}\n"
        response += f"**Seria:** {tournament_data.get('serie', {}).get('name', 'Brak')}\n"

        # Daty
        begin_at = tournament_data.get('begin_at')
        end_at = tournament_data.get('end_at')
        if begin_at:
            begin_date = datetime.datetime.strptime(begin_at, "%Y-%m-%dT%H:%M:%SZ")
            response += f"**Data rozpoczęcia:** {begin_date.strftime('%d.%m.%Y %H:%M')}\n"
        if end_at:
            end_date = datetime.datetime.strptime(end_at, "%Y-%m-%dT%H:%M:%SZ")
            response += f"**Data zakończenia:** {end_date.strftime('%d.%m.%Y %H:%M')}\n"

        # Pula nagród
        prizepool = tournament_data.get('prizepool')
        if prizepool:
            response += f"**Pula nagród:** {prizepool}\n"

        # Status
        response += f"**Status:** {tournament_data.get('status', 'Brak')}\n"

        # Liczba drużyn
        response += f"**Liczba drużyn:** {tournament_data.get('number_of_teams', 'Brak')}\n"

        await ctx.respond(response)
    else:
        await ctx.respond(f"Nie udało się pobrać szczegółów turnieju: {result['error']}")


@bot.slash_command(
    name="add_player",
    description="Dodaje zawodnika do turnieju"
)
async def add_player(ctx, tournament_id: str, player_name: str, team_name: str):
    await ctx.defer()
    result = add_player_to_tournament(tournament_id, player_name, team_name)

    if result["success"]:
        embed = discord.Embed(
            title="✅ Pomyślnie dodano zawodnika",
            color=discord.Color.green()
        )
        embed.add_field(name="Zawodnik", value=player_name, inline=True)
        embed.add_field(name="Drużyna", value=team_name, inline=True)
        embed.add_field(name="ID", value=result["player_id"], inline=True)
        embed.add_field(name="Turniej", value=result["tournament_name"], inline=False)

        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Błąd podczas dodawania zawodnika",
            description=result["error"],
            color=discord.Color.red()
        )
        await ctx.respond(embed=embed)


@bot.slash_command(
    name="tournament_roster",
    description="Pokazuje wszystkie drużyny i zawodników w turnieju"
)
async def tournament_roster(ctx, tournament_id: str):
    await ctx.defer()
    result = get_tournament_roster(tournament_id)

    if result["success"]:
        response = "**🎮 SKŁADY DRUŻYN W TURNIEJU**\n\n"

        for team in result["data"]:
            response += f"__**{team['team_name']}**__\n"
            response += f"Status: {team['status']}\n"
            response += "Zawodnicy:\n"

            for player in team["players"]:
                response += f"• {player['name']} "
                if player['role'] != "N/A":
                    response += f"({player['role']}) "
                if player['nationality'] != "N/A":
                    response += f"🏳️ {player['nationality']}"
                response += "\n"

            response += "\n"

        await ctx.respond(response)
    else:
        await ctx.respond(f"❌ Nie udało się pobrać składów drużyn: {result['error']}")
