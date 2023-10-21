import hikari, lightbulb, re, mysql.connector

from HackNottsVerification.bot import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, timezone

plugin = lightbulb.Plugin("schedule", default_enabled_guilds=1147945134831440082)

# Scheduler set up, timezone is London
scheduler = AsyncIOScheduler() # Has to be async for the bot
scheduler.configure(timezone=timezone.utc)
scheduler.start()

async def post_event(id: str, channel_id: int = 1148348825153572874, preview: bool = False) -> bool:
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

    # `Name`, `Description`, `StartTime`, `Delta`, `Location`, `URL`, `Author`, `AuthorURL`, `Colour`
    sql = "SELECT * FROM `Schedule` WHERE `Name` = %s"
    db_cursor.execute(sql, (id,))
    try:
        result = db_cursor.fetchall()[0]
    except IndexError:
        db.close()
        return False # The ID was not found

    if result['URL'] is None:
        url = "https://www.hacknotts.com/schedule/" # Default URL if none is give
    else:
        url = result['URL']

    if result['Colour'] is None:
        colour = "F5F5DC" # Default colour if none is given
    else:
        colour = result['Colour']

    embed = hikari.Embed(
        title=result['Name'],
        url=url,
        colour=colour, # Default hacknotts 
        description=result['Description'],
        timestamp=result['StartTime'].astimezone(timezone.utc),
    )

    if result['Location'] is not None:
        embed.add_field(name="Location", value=result['Location'])
    if result['Author'] is not None:
        embed.set_author(name=result['Author'], url=result['AuthorURL'])

    embed.set_footer(text="HackNotts 2023 ½")

    if not preview:
        # Set EventPassed to 1 to show the event has been posted
        sql = "UPDATE `Schedule` SET `EventPassed` = 1 WHERE `Name` = %s"
        db_cursor.execute(sql, (id,))
        db.commit()
        # Ping everone outside of the embed, you cannot ping roles inside of the embed!
        await plugin.bot.rest.create_message(channel=channel_id, content="<@&1147945134831440085>", mentions_everyone=True, user_mentions=True, role_mentions=True)

    await plugin.bot.rest.create_message(channel=channel_id, embed=embed)
    db.close()
    return True # Eveything worked fine

def database_interaction(event, mode="insert", old_name=None) -> bool:
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

    if mode == "insert":
        sql = "INSERT INTO `Schedule` (`Name`, `Description`, `StartTime`, `Delta`, `Location`, `URL`, `Author`, `AuthorURL`, `Colour`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (event['Name'], event['Description'], event['StartTime'], event['Delta'], event['Location'], event['URL'], event['Author'], event['AuthorURL'], event['Colour'])
    elif mode == "update":
        if old_name is None:
            ID = event['Name']
        else:
            ID = old_name
        sql = "UPDATE `Schedule` SET `Name` = %s, `Description` = %s, `StartTime` = %s, `Delta` = %s, `Location` = %s, `URL` = %s, `Author` = %s, `AuthorURL` = %s, `Colour` = %s WHERE `Name` = %s"
        values = (event['Name'], event['Description'], event['StartTime'], event['Delta'], event['Location'], event['URL'], event['Author'], event['AuthorURL'], event['Colour'], ID)

    try:
        db_cursor.execute(sql, values)
        db.commit()
        db.close()
        return True
    except mysql.connector.errors.IntegrityError:
        return False

def flush() -> list:
    scheduler.remove_all_jobs() # Removes all jobs from the scheduler
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
    sql = "SELECT `Name`, `Delta` FROM `Schedule` WHERE `EventPassed` = 0"
    db_cursor.execute(sql)
    
    jobs = []
    i = 1
    for row in db_cursor:
        scheduler.add_job(post_event, 'date', run_date=row['Delta'], id=row['Name'], args=[row['Name']])
        jobs.append(f"{i}) {row['Name']} TBA @ {row['Delta']}\n")
        i += 1

    db.close()
    return jobs # A list of jobs with datetimes in the form: i) <event name> TBA @ <datetime>

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.option("name", "Name of the event", required=True)
@lightbulb.option("description", "Description of the event, markdown is fine to use!", required=True)
@lightbulb.option("datetime", "Must be in the format: yyyy-mm-dd hh:mm 24 hour **UTC**", required=True)
@lightbulb.option("author", "Name of the organiser for the event", required=False)
@lightbulb.option("author_url", "The url for the organiser", required=False)
@lightbulb.option("location", "Location of the event", required=False)
@lightbulb.option("delta", "The number of minuets to make the announcement before the start time", required=False)
@lightbulb.option("url", "The url for the event, default is the HackNotts schedule page", required=False)
@lightbulb.option("colour", "The hex colour for the embed, default is 'F5F5DC'", required=False)
@lightbulb.command("new_event", "Creates a new scheduled event embed", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def new_event(ctx: lightbulb.SlashContext) -> None:
    event = {} # Where all the event details will be stored
    event['Author'] = ctx.options.author            # The author of the embed
    event['AuthorURL'] = ctx.options.author_url     # The url for the author
    event['Name'] = ctx.options.name                # This is the ID for the scheduler
    event['Description'] = ctx.options.description  # Description of the event
    event['Location'] = ctx.options.location        # Location
    event['URL'] = ctx.options.url                  # URL link for the title
    event['Colour'] = ctx.options.colour            # The colour of the embed

    try:
        if re.search("^[a-fA-F0-9]+$", event['Colour']) is None or len(event['Colour']) != 6:
            await ctx.respond(f"The colour **#{event['Colour'].upper()}** is not a 6 diget hex code")
            return
    except TypeError:
        pass

    # Is the datetime in the correct format?
    try:
        date = ctx.options.datetime.split()[0].split('-')
        time = ctx.options.datetime.split()[1].split(':')
    except IndexError:
        await ctx.respond(f"The datetime **{ctx.options.datetime}** is not in the format yyyy-mm-dd hh:mm")
        return 

    try:
        stamp = datetime(
            year=int(date[0]), month=int(date[1]), day=int(date[2]), 
            hour=int(time[0]), minute=int(time[1]), tzinfo=timezone.utc
            )
        event['StartTime'] = stamp
    except ValueError as error:
        await ctx.respond(error.args[0])
        return

    # Is it a datetime in the past
    if event['StartTime'] < datetime.now(tz=timezone.utc):
        await ctx.respond(f"The datetime **{event['StartTime']}** is in the past!")
        return

    # Time for the announcement to be said
    if ctx.options.delta is None:
        event['Delta'] = event['StartTime']
    else:
        event['Delta'] = event['StartTime'] - timedelta(minutes=int(ctx.options.delta))

    if event['Delta'] < datetime.now(tz=timezone.utc):
        await ctx.respond(f"The delta is in the past!")
        return

    if database_interaction(event=event):
        scheduler.add_job(post_event, 'date', run_date=event['Delta'], id=event['Name'], args=[event['Name']])
        await ctx.respond(f"Event: **{event['Name']}** was added and will be announced at: {event['Delta']}")
    else:
        await ctx.respond(f"Event: **{event['Name']}** already exists!")

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.option("name", "Name of the event you want to update", required=True)
@lightbulb.option("new_name", "New name of the event", required=False)
@lightbulb.option("author", "Name of the organiser for the event", required=False)
@lightbulb.option("author_url", "The url for the organiser", required=False)
@lightbulb.option("description", "Description of the event, markdown is fine to use!", required=False)
@lightbulb.option("location", "Location of the event", required=False)
@lightbulb.option("datetime", "Must be in the format: yyyy-mm-dd hh:mm 24 hour **UTC**", required=False)
@lightbulb.option("delta", "The number of minuets to make the announcement before the start time", required=False)
@lightbulb.option("url", "The url for the event, default is the HackNotts schedual page", required=False)
@lightbulb.option("colour", "The hex colour for the embed, default is 'F5F5DC'", required=False)
@lightbulb.command("update_event", "Updates an event previously set, to clear a feild type a 0", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def update_event(ctx: lightbulb.SlashContext) -> None:
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

    sql = "SELECT * FROM `Schedule` WHERE `Name` = %s"
    db_cursor.execute(sql, (ctx.options.name,))
    
    try:
        event: dict = db_cursor.fetchall()[0] # Was there an event found?
        db.close()
        event.pop('ID', None)           # Remove unwanted columns
        event.pop('EventPassed', None)
    except IndexError:
        await ctx.respond(f"There is no event named **{ctx.options.name}**")
        return

    # Update the event as needed
    if ctx.options.author is not None:
        if ctx.options.author == '0':
            event['Author'] = None # Clear author
        else:
            event['Author'] = ctx.options.author

    if ctx.options.authour_url is not None:
        if ctx.options.author_url == '0':
            event['AuthorURL'] = None # Clear author URL
        else:
            event['AuthorURL'] = ctx.options.authour_url

    if ctx.options.description is not None:
        if ctx.options.description == '0':
            await ctx.respond("The description is mandatory")
            return
        event['Description'] = ctx.options.description

    if ctx.options.location is not None:
        if ctx.options.location == '0':
            event['Location'] = None # Clear location
        else:
            event['Location'] = ctx.options.location

    if ctx.options.datetime is not None:
        if ctx.options.datetime == '0':
            await ctx.respond("The datetime is mandatory")
            return
        # Is it a datetime in the past
        if event['StartTime'].astimezone(timezone.utc) < datetime.now(tz=timezone.utc):
            await ctx.respond(f"The datetime **{event['StartTime']}** is in the past!")
            return

    if ctx.options.delta is not None:
        event['Delta'] = event['StartTime'] - timedelta(minutes=int(ctx.options.delta))

    if event['Delta'].astimezone(timezone.utc) < datetime.now(tz=timezone.utc):
        await ctx.respond(f"The delta is in the past!")
        return

    if ctx.options.url is not None:
        if ctx.options.url == '0':
            event['URL'] = None # Clear URL
        else:
            event['URL'] = ctx.options.url

    if ctx.options.colour is not None:
        if ctx.options.colour == '0':
            event['Colour'] = None # Clear colour
        else:
            event['Colour'] = ctx.options.colour
            if re.search("^[a-fA-F0-9]+$", event['Colour']) is None or len(event['Colour']) != 6:
                await ctx.respond(f"The colour **#{event['Colour'].upper()}** is not a 6 diget hex code")
                return

    if ctx.options.new_name is not None:
        if ctx.options.new_name == '0':
            await ctx.respond("The name is mandatory") # Cannot clear name
            return
        event['Name'] = ctx.options.new_name
        database_interaction(event=event, mode="update", old_name=ctx.options.name) # Update the current data
    else:
        database_interaction(event=event, mode="update") # Update the current data

    # Update the scheduler
    scheduler.remove_job(ctx.options.name)
    scheduler.add_job(post_event, 'date', run_date=event['Delta'], id=event['Name'], args=[event['Name']])
    await ctx.respond(f"Event **{ctx.options.name}** has been updated")

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.command("list_active", "Lists all active events", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def list_active(ctx: lightbulb.SlashContext) -> None:
    jobs = scheduler.get_jobs()
    if len(jobs) == 0:
        await ctx.respond("There are no active events")
    else:
        text = ''.join([f"{x+1}) {jobs[x].id} TBA @ {jobs[x].trigger.run_date}\n" for x in range(len(jobs))])
        await ctx.respond(text)

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.command("list_past", "Lists all past events", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def list_past(ctx: lightbulb.SlashContext) -> None:
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

    sql = "SELECT `Name` FROM `Schedule` WHERE `EventPassed` = 1"
    db_cursor.execute(sql)
    result = db_cursor.fetchall()

    if result is None:
        await ctx.respond("There are no past events yet")
    else:
        events = ''.join([f"{x+1}) {result[x]['Name']}\n" for x in range(len(result))])
        await ctx.respond("There are the following past events:\n"+events)

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.option("id", "This is the name of the event that was entered, get all names with `/list_all`")
@lightbulb.command("preview", "Preview an event", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def preview(ctx: lightbulb.SlashContext) -> None:
    job = scheduler.get_job(job_id=ctx.options.id)
    if job is None:
        await ctx.respond(f"There was no event found called \"**{ctx.options.id}**\"")
        return
    else:
        await ctx.respond(f"Event **{ctx.options.id}** will look like the following:")
        await post_event(ctx.options.id, ctx.channel_id, True)

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.option("name", "The name of the event you wish to delete")
@lightbulb.command("delete_event", "This will delete an event from the database, cannot be undone!", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def delete(ctx: lightbulb.SlashContext) -> None:
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

    sql = "DELETE FROM `Schedule` WHERE `Name` = %s"
    db_cursor.execute(sql, (ctx.options.name,))
    db.commit()
    db.close()

    if db_cursor.rowcount == 0:
        await ctx.respond(f"No event found with name **{ctx.options.name}**")
    else:
        flush()
        await ctx.respond(f"Event **{ctx.options.name}** has been deleted")

@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.command("flush_events", "Reloads all events in the schedule", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def flush_all(ctx: lightbulb.SlashContext) -> None:
    jobs  = flush()
    if jobs == []:
        await ctx.respond("All events flushed.\nThere are no active events")
    else:
        await ctx.respond(f"All events flushed.\n{''.join(jobs)}")

def load(bot: Bot) -> None:
    flush()
    bot.add_plugin(plugin)

def unload(bot: Bot) -> None:
    scheduler.shutdown()
    bot.remove_plugin("schedule")