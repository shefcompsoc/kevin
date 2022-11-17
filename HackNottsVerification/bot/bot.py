import logging, hikari, lightbulb

from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
from HackNottsVerification import __version__

class Bot(lightbulb.BotApp):
    def __init__(self) -> None:
        self._extensions = [p.stem for p in Path(".").glob("./HackNottsVerification/bot/extensions/*.py")]
        self.scheduler = AsyncIOScheduler()
        self.scheduler.configure(timezone=utc)

        with open("./secrets/discord", mode="r", encoding="utf-8") as f:
            token = f.read().strip()

        super().__init__(
            token = token,
            #default_enabled_guilds=(1023695785495363584),
            help_slash_command=True,
            intents = hikari.Intents.ALL # For debugging just use all cos why not
            #intents = hikari.Intents.GUILD_MEMBERS # For sending messages
        )

    def run(self) -> None:
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)            # When the bot it starting
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)              # When the bot started
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)            # When the bot is stopping
        self.event_manager.subscribe(hikari.StoppedEvent, self.on_stopped)              # When the bot stopped
        #self.event_manager.subscribe(lightbulb.CommandErrorEvent, self.on_error)        # Global error handler uncomment for actual release
        self.event_manager.subscribe(hikari.GuildMessageCreateEvent, self.on_message)   # Whenever a message is sent
        self.event_manager.subscribe(hikari.MemberDeleteEvent, self.on_leave)

        super().run(
            activity=hikari.Activity(
                name=f"Verification Bot | Version {__version__}", # displays on the side, discord presence
                type=hikari.ActivityType.PLAYING
            )
        )

    async def on_starting(self, event: hikari.StartingEvent) -> None:
        for ext in self._extensions:
            self.load_extensions(f"HackNottsVerification.bot.extensions.{ext}")
            logging.info(f"\"{ext}\" extension loaded")

    async def on_started(self, event: hikari.StartedEvent) -> None:
        self.scheduler.start()
        await self.update_presence(status=hikari.Status.ONLINE)
        logging.info("BOT READY")

    async def on_stopping(self, event: hikari.StoppingEvent) -> None:
        self.scheduler.shutdown()
        await self.update_presence(status=hikari.Status.DO_NOT_DISTURB)
        logging.info("BOT STOPPING")

    async def on_stopped(self, event:hikari.StoppedEvent) -> None:
        logging.info("BOT STOPPED")

    async def on_error(self, event:lightbulb.CommandErrorEvent) -> None:
        logging.warning(f"{event.context.author} tried using the command \"{event.context.command.name}\" with error \"{event.exception}\"")
        await event.context.respond(f"Error moment: {event.exception}", flags=hikari.MessageFlag.EPHEMERAL)

        if str(event.exception) != "You are not the owner of this bot":
            me = await self.rest.create_dm_channel(427401640061042689)
            await me.send(event.exception)

    async def on_message(self, event:hikari.GuildMessageCreateEvent) -> None:
        channel_id = (1026601514921381889) # Tuple of channel ID's to be nuked
        try:
            if event.channel_id in channel_id and event.author_id != 427401640061042689: # Is it not me? 
                logging.info(f"Deleted message in verify channel: '{event.message.content}'")
                await self.rest.delete_message(channel_id, event.message_id) 
                user = await self.rest.create_dm_channel(event.member.id)
                await user.send("You cannot send normal messages in the verify channel. It is for verify commands only")
                await user.send(f"The message: '{event.message.content}' was automatically deleted")
        except TypeError:
            pass

    async def on_leave(self, event:hikari.MemberDeleteEvent) -> None:
        logging.info(f"{event.user.username}#{event.user.discriminator} left the server")
