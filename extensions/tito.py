import aiohttp, discord, logging, utils

from discord.ext import commands, tasks
from env import env


class Tito(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = utils.TitoAPI(env.TITO_TOKEN, env.TITO_ACCOUNT_SLUG, env.TITO_EVENT_SLUG)
        self.attendees: dict[str, int] = {}

    def cog_unload(self):
        self.pull_answers.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.pull_answers.start()

    @tasks.loop(seconds=60.0)
    async def pull_answers(self):
        answers = await self.api.fetch_question_answers(env.TITO_QUESTION_SLUG)
        for a in answers:
            self.attendees[a.response] = a.ticket_id

    # TODO: allow to be used as user command
    @commands.slash_command(description="Checks if the user has a ticket and gives them the attendee role if they do.")
    @commands.guild_only()
    async def verify(self, ctx: discord.ApplicationContext, *, user: discord.Member = None):
        # Reject normal users from verifying other users
        if user is not None \
          and user.id != ctx.author.id \
          and not utils.is_volunteer(ctx.author):
            logging.warning(f"User {ctx.author.name} attempted to user a forbidden command.")
            return await ctx.respond("✋ Only organisers can verify other users.", ephemeral=True)
            
        # Check for a ticket in the cache
        user = user or ctx.author
        ticket = self.attendees.get(user.name)
        if ticket is None:
            # TODO: maybe query the API directly?
            logging.warning(f"Attempted to verify user {user.name} but could not find a valid ticket.")
            return await ctx.respond(f"🤔 Sorry, I can't find a ticket for `{user.name}`. If one was bought recently, please wait a bit and then try again.", ephemeral=True)
        
        # Verify the user
        await user.add_roles(ctx.guild.get_role(env.DISCORD_ATTENDEE_ROLE_ID))
        await ctx.respond(f"✅ Boom! I found a ticket for `{user.name}`.", ephemeral=True)
        logging.info(f"Successfully verified user {user.name}.")

    # Allow use as user command
    @commands.slash_command(description="Fetches the ticket ID for a user, if they have one.")
    @commands.guild_only()
    async def ticketof(self, ctx: discord.ApplicationContext, user: discord.Member):
        # Normal users can't do this
        if not utils.is_volunteer(ctx.author):
            logging.warning(f"User {ctx.author.name} attempted to user a forbidden command.")
            return await ctx.respond("✋ Only organisers can do this.", ephemeral=True)

        ticket = self.attendees.get(user.name)
        if ticket is None:
            # TODO: maybe query the API directly?
            return await ctx.respond(f"🤔 Sorry, I can't find a ticket for `{user.name}`. If one was bought recently, please wait a bit and then try again.", ephemeral=True)
        
        await ctx.respond(f"ℹ️ I found a ticket for `{user.name}`. Their ticket ID is `{ticket}`.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id != env.DISCORD_GUILD_ID:
            return
        
        if member.bot:
            return
        
        ticket = self.attendees.get(member.name)
        if ticket is None:
            return
        
        await member.add_roles(member.guild.get_role(env.DISCORD_ATTENDEE_ROLE_ID))
        logging.info(f"Verified user {member.name} on join.")

def setup(bot):
    bot.add_cog(Tito(bot))
    logging.info("Added cog: tito")