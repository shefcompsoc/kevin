import discord, logging

from env import env


logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S", 
    encoding="utf-8", 
    level=logging.DEBUG)

intents = discord.Intents.default()
intents.members = True

bot = discord.Bot(intents=intents)

if __name__ == "__main__":
    bot.load_extension(f"extensions.ping")
    bot.load_extension(f"extensions.tito")
    bot.run(env.DISCORD_TOKEN)