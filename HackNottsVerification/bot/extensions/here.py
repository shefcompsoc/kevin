import hikari, lightbulb, mysql.connector

from HackNottsVerification.bot import Bot

plugin = lightbulb.Plugin("here", default_enabled_guilds=1147945134831440082)

@plugin.command
@lightbulb.command("here", "Use this to get the 'I was here' role!", auto_defer = True, ephemeral = True)
@lightbulb.implements(lightbulb.SlashCommand)
async def here(ctx: lightbulb.SlashContext):
    role_id = 1147945134831440084
    with open("./secrets/sqlserver_pass", "r") as file:
        sql_pass = file.read().strip()

    with open("./secrets/sqlserver_user", "r") as file:
        sql_user = file.read().strip()

    db = mysql.connector.connect(
        host="localhost",
        user=sql_user,
        password=sql_pass,
        database="HackNotts2"
    )
    db_cursor = db.cursor(dictionary=True)
    sql = "SELECT * FROM `People` WHERE `DiscordTag` = %s"
    db_cursor.execute(sql, (ctx.user.username,))
    try:
        result: dict = db_cursor.fetchall()[0]
    except IndexError:
        await ctx.respond("You are not in the database")
        return
    db.close()

    if result['CheckedIn'] == 0:
        await ctx.respond("You have not checked in yet!")
    elif result['CheckedIn'] == 1:
        await plugin.bot.rest.add_role_to_member(ctx.guild_id, ctx.user.id, role_id)
        await ctx.respond("*You're in*")
    else:
        ctx.respond("An error occured! Try again later :smiley:")

def load(bot: Bot) -> None:
    bot.add_plugin(plugin)

def unload(bot: Bot) -> None:
    bot.remove_plugin("here")
