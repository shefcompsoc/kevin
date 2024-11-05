import logging

from discord import ApplicationContext
from discord.ext import commands


@commands.slash_command(description="Helps check if the bot is online.")
async def ping(ctx: ApplicationContext):
    await ctx.respond(f"🏓 Pong! Latency is `{ctx.bot.latency * 1000:.2f} ms`", ephemeral=True)

def setup(bot):
    bot.add_application_command(ping)
    logging.info("Added command: ping")