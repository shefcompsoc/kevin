import hikari, lightbulb

from HackNottsVerification.bot import Bot

plugin = lightbulb.Plugin("Admin")

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.option("plugin", "The name of the extension to be removed", required=True)
@lightbulb.command("disable", "Disable an extention", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def admin_only(ctx: lightbulb.SlashContext) -> None:
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
async def admin_only(ctx: lightbulb.SlashContext) -> None:
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
async def admin_only(ctx: lightbulb.SlashContext) -> None:
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
@lightbulb.command("showall", "Show all extensions", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def admin_only(ctx: lightbulb.SlashContext) -> None:
    raw = plugin.bot.extensions
    plugins = []
    for i in range(len(raw)):
        plugins.append(raw[i].split('.')[-1])

    await ctx.respond(plugins)

def load(bot: Bot) -> None:
    bot.add_plugin(plugin)

def unload(bot: Bot) -> None:
    bot.remove_plugin("Admin")
