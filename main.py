from bot.client import bot
from libs.config import Config


def main():
    """
    Główna funkcja uruchamiająca bota Discord
    """
    try:
        print("Uruchamianie bota...")
        bot.run(Config.DISCORD_TOKEN)
    except Exception as e:
        print(f"Wystąpił błąd podczas uruchamiania bota: {str(e)}")
        raise


if __name__ == "__main__":
    main()