import logging, hikari, lightbulb

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

class Bot(lightbulb.BotApp):
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.scheduler.configure(timezone=utc)

        with open("./secrets/oar", mode="r", encoding="utf-8") as f:
            token = f.read().strip()

        super().__init__(
            token = token,
            help_slash_command=False,
            intents = hikari.Intents.ALL
        )

    def run(self) -> None:
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)            # When the bot it starting
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)              # When the bot started
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)            # When the bot is stopping
        self.event_manager.subscribe(hikari.StoppedEvent, self.on_stopped)              # When the bot stopped
        self.event_manager.subscribe(lightbulb.CommandErrorEvent, self.on_error)        # Global error handler uncomment for actual release
        self.event_manager.subscribe(hikari.GuildMessageCreateEvent, self.on_message)   # Whenever a message is sent
        self.event_manager.subscribe(hikari.MemberDeleteEvent, self.on_leave)

        with open("./HackNottsVerification/version.txt", "r") as file:
            __version__ = file.read().strip()

        super().run(
            activity=hikari.Activity(
                name=f"Verification Bot | Version {__version__}", # displays on the side, discord presence
                type=hikari.ActivityType.PLAYING
            )
        )

    async def on_starting(self, event: hikari.StartingEvent) -> None:
        self.load_extensions_from("./HackNottsVerification/bot/extensions") # Load all extensions
        logging.info("All extensions loaded")

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
        channel_id = 977229878850097203 # Channel ID's to be nuked
        try:
            if event.channel_id == channel_id and event.author_id != 427401640061042689: # Is it not me?
                logging.info(f"Deleted message in verify channel: '{event.message.content}'")
                await self.rest.delete_message(channel_id, event.message_id) 
                user = await self.rest.create_dm_channel(event.member.id)
                await user.send("You cannot send normal messages in the verify channel. It is for verify commands only")
                await user.send(f"The message: '{event.message.content}' was automatically deleted")
        except TypeError:
            pass

    async def on_leave(self, event:hikari.MemberDeleteEvent) -> None:
        logging.info(f"{event.user.username}#{event.user.discriminator} left the server")