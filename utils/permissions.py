import discord

from env import env


def is_attendee(user: discord.Member) -> bool:
    return any(role.id == env.DISCORD_ATTENDEE_ROLE_ID for role in user.roles)

def is_volunteer(user: discord.Member) -> bool:
    return any(role.id == env.DISCORD_ORGANISER_ROLE_ID or role.id == env.DISCORD_VOLUNTEER_ROLE_ID for role in user.roles)