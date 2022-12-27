import hikari, lightbulb

from HackNottsVerification.bot import Bot

plugin = lightbulb.Plugin("Admin", default_enabled_guilds=977197096094564453)

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.option("plugin", "The name of the extension to be removed", required=True)
@lightbulb.command("disable", "Disable an extention", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def disable(ctx: lightbulb.SlashContext) -> None:
    try:
        plugin.bot.unload_extensions(f"HackNottsVerification.bot.extensions.{ctx.options.plugin}")
        await plugin.bot.sync_application_commands()
        await ctx.respond(f"The extension **{ctx.options.plugin}** has been disabled")
    except lightbulb.errors.ExtensionNotLoaded:
        await ctx.respond(f"The extension **{ctx.options.plugin}** was already disabled")
    except lightbulb.errors.ExtensionNotFound:
        await ctx.respond(f"The extension **{ctx.options.plugin}** could not be found")

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.option("plugin", "The name of the extension to be enabled", required=True)
@lightbulb.command("enable", "Enable an extension", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def enable(ctx: lightbulb.SlashContext) -> None:
    try:
        plugin.bot.load_extensions(f"HackNottsVerification.bot.extensions.{ctx.options.plugin}")
        await plugin.bot.sync_application_commands()
        await ctx.respond(f"The extension **{ctx.options.plugin}** has been enabled")
    except lightbulb.errors.ExtensionAlreadyLoaded:
        await ctx.respond(f"The extension **{ctx.options.plugin}** was already enabled")
    except lightbulb.errors.ExtensionNotFound:
        await ctx.respond(f"The extension **{ctx.options.plugin}** could not be found")

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.option("plugin", "The name of the extension to be enabled", required=True)
@lightbulb.command("reload", "Reload an extension", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def reload(ctx: lightbulb.SlashContext) -> None:
    try:
        try:
            plugin.bot.unload_extensions(f"HackNottsVerification.bot.extensions.{ctx.options.plugin}")
        except lightbulb.errors.ExtensionNotLoaded:
            pass

        try:
            plugin.bot.load_extensions(f"HackNottsVerification.bot.extensions.{ctx.options.plugin}")
        except lightbulb.errors.ExtensionAlreadyLoaded:
            pass
        await plugin.bot.sync_application_commands()
        await ctx.respond(f"The extension **{ctx.options.plugin}** has been reloaded")
    except lightbulb.errors.ExtensionNotFound:
        await ctx.respond(f"The extension **{ctx.options.plugin}** could not be found")

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.option("activity", "Can be 'Playing', 'Listening', 'Watching' or 'Competing'", required=False)
@lightbulb.option("status", "Can be 'Online', 'Invisible', 'DND' or 'Idle'", required=False)
@lightbulb.command("update_presence", "Update the presence of the bot", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def update_presence(ctx: lightbulb.SlashContext) -> None:
    with open("./HackNottsVerification/version.txt", "r") as file:
            __version__ = file.read().strip()

    if ctx.options.activity is not None:
        match ctx.options.activity.lower():
            case "playing":
                await plugin.bot.update_presence(activity=hikari.Activity(type=hikari.ActivityType.PLAYING, name=f"Verification Bot | Version {__version__}"))
            case "1":
                await plugin.bot.update_presence(activity=hikari.Activity(type=hikari.ActivityType.PLAYING, name=f"Verification Bot | Version {__version__}"))
            case "listening":
                await plugin.bot.update_presence(activity=hikari.Activity(type=hikari.ActivityType.LISTENING, name=f"Verification Bot | Version {__version__}"))
            case "2":
                await plugin.bot.update_presence(activity=hikari.Activity(type=hikari.ActivityType.LISTENING, name=f"Verification Bot | Version {__version__}"))
            case "watching":
                await plugin.bot.update_presence(activity=hikari.Activity(type=hikari.ActivityType.WATCHING, name=f"Verification Bot | Version {__version__}"))
            case "3":
                await plugin.bot.update_presence(activity=hikari.Activity(type=hikari.ActivityType.WATCHING, name=f"Verification Bot | Version {__version__}"))
            case "Competing":
                await plugin.bot.update_presence(activity=hikari.Activity(type=hikari.ActivityType.COMPETING, name=f"Verification Bot | Version {__version__}"))
            case "4":
                await plugin.bot.update_presence(activity=hikari.Activity(type=hikari.ActivityType.COMPETING, name=f"Verification Bot | Version {__version__}"))

    if ctx.options.status is not None:
        match ctx.options.status.lower():
            case "online":
                await plugin.bot.update_presence(status=hikari.Status.ONLINE)
            case "1":
                await plugin.bot.update_presence(status=hikari.Status.ONLINE)
            case "invisible":
                await plugin.bot.update_presence(status=hikari.Status.OFFLINE)
            case "2":
                await plugin.bot.update_presence(status=hikari.Status.OFFLINE)
            case "dnd":
                await plugin.bot.update_presence(status=hikari.Status.DO_NOT_DISTURB)
            case "3":
                await plugin.bot.update_presence(status=hikari.Status.DO_NOT_DISTURB)
            case "idle":
                await plugin.bot.update_presence(status=hikari.Status.IDLE)
            case "4":
                await plugin.bot.update_presence(status=hikari.Status.IDLE)

    await ctx.respond(f"Done")

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.command("showall", "Show all extensions", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def showall(ctx: lightbulb.SlashContext) -> None:
    raw = plugin.bot.extensions
    plugins = []
    for i in range(len(raw)):
        plugins.append(raw[i].split('.')[-1])

    await ctx.respond(plugins)

def load(bot: Bot) -> None:
    bot.add_plugin(plugin)

def unload(bot: Bot) -> None:
    bot.remove_plugin("Admin")
