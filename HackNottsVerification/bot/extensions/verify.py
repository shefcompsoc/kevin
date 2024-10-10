import re, hikari, lightbulb, logging, mysql.connector

from HackNottsVerification.bot import Bot

# HackNotts Server
server_info = {
    'server_id': 1257068902773559326,
    'verified': 1293626063045525596,
    'Attendee': 1286310578142445639,
    'Hacker': 1286310578142445639,
    'Volunteer': 1257069700207087727,
    'Sponsor': 1286316167937396850,
    'Organiser': 1257069655722299422,
    'Here': 1293625793754435584,
    'logs': 1293625679413383308
} # Role ID's

async def user_verify(user, ID: int, ref: str):
    ref = ref.upper()

    with open("./secrets/sqlserver_pass", "r") as file:
        sql_pass = file.read().strip()

    with open("./secrets/sqlserver_user", "r") as file:
        sql_user = file.read().strip()

    try:
        db = mysql.connector.connect(
        host="localhost",
        user=sql_user,
        password=sql_pass,
        database="HackNotts3"
        )

        db_cursor = db.cursor()
    except mysql.connector.DatabaseError:
        return None

    sql = "SELECT `ID`, `DiscordTag`, `TicketType`, `Verified`, `CheckedIn` FROM `People` WHERE `TicketRef` = %s"
    db_cursor.execute(sql, (ref,))
    try:
        result = db_cursor.fetchall()[0]
    except IndexError: # The ticket reference could not be found in the database
        result = None

    flag = 0 # Have they tried using someone elses code
    verif = False
    if result is None: # There was no reference found
        message = f"The ticket reference \'**{ref}**\' does not seem to be in our database. Please check you have entered it correctly. It should be 6 characters ***including*** the hyphen."
    elif result[3] == 1 and str(result[1]) == str(user): # The verified username is 1 and the discord usernames match
        message = f"You are already verified!"
    elif result[3] == 1: # Verified is 1 but discord usernames dont match
        message = f"It appears that the ticket with reference \'**{ref}**\' is already registered with a user. A message has been automatically sent to an organiser who will contact you shortly to resolve this issue."
        flag = 1
    elif result[1] is not None: # There is something in the discord username
        if str(result[1]) == str(user): # Verified is not 1 and usernames match
            verif = True
        else:
            message = f"There is a linked Discord username to this ticket reference \'**{ref}**\' which does not match yours. If you entered your Discord username when assigning your ticket, double check that it has been spelt correctly. If it does not match then you will not be able to verify yourself. You can update your information via the ticket confirmation email."
            flag = 2
    elif result[1] is None: # There is no discord username so must be verified
        verif = True

    if verif is True: # Verify user and update record
        try:
            sql = "UPDATE `People` SET `Verified` = 1, `DiscordTag` = %s, `DiscordID` = %s WHERE `ID` = %s" # Set user to be verified and set their username
            db_cursor.execute(sql, (user, ID, result[0]))
            db.commit()

            if result[4] == 1: # They are checked in so give the 'I was here' role
                await plugin.app.rest.add_role_to_member(server_info['server_id'], ID, server_info['Here'])

            logging.info(f"User '{user}' has been manually verified with reference \'{ref}\' as '{result[2]}'")
            message = f"You have been verified with ticket type: **{result[2]}** and have accompanying roles assigned to you. Thank you!"

        except mysql.connector.errors.IntegrityError: # Probably a discord username is in the database
            message = f"Your Discord username is already assigned to a ticket reference. A message has been sent to an organiser and they will be in touch with you to resolve this issue."
            flag = 3

    db.close()
    try:
        return (message, flag, str(result[2])) # Message is the text that the person will see as an ephemeral
    except TypeError:
        return(message, flag, None)


async def auto_verify(tag: str, ID: int):
    with open("./secrets/sqlserver_pass", "r") as file:
        sql_pass = file.read().strip()

    with open("./secrets/sqlserver_user", "r") as file:
        sql_user = file.read().strip()

    try:
        db = mysql.connector.connect(
        host="localhost",
        user=sql_user,
        password=sql_pass,
        database="HackNotts3"
        )

        db_cursor = db.cursor()
    except mysql.connector.DatabaseError:
        return 0

    sql = "SELECT `ID`, `TicketRef`, `TicketType`, `Verified`, `CheckedIn` FROM `People` WHERE `DiscordTag` = %s"
    db_cursor.execute(sql, (tag,))
    try:
        result = db_cursor.fetchall()[0]
    except IndexError:
        result = None

    _type = None # Ticket type eg 'Hacker'
    _id = None # ID of the row in the database
    flag = False # Used if they join and their discord username is already verified
    if result is None:
        flag = None # Don't do anything 
    elif result[3] == 1:
        flag = True
    else:
        _id = result[0]
        _type = str(result[2])
        sql = "UPDATE `People` SET `Verified` = 1, `DiscordID` = %s WHERE `ID` = %s" # Set user to be verified and set their tag
        db_cursor.execute(sql, (ID, _id)) # ID = Dsicord ID, _id = database ID
        db.commit()

        if result[4] == 1: # They are checked in so give the 'I was here' role
            await plugin.app.rest.add_role_to_member(server_info['server_id'], ID, server_info['Here'])

        logging.info(f"User: {tag} has been auto verified with ticket reference '{result[1]}' as '{_type}'")
        
    db.close()
    return (flag, _id, _type) # Is the person already verified?


plugin = lightbulb.Plugin("verify")

@plugin.listener(hikari.MemberCreateEvent)
async def on_join(event: hikari.MemberCreateEvent) -> None:
    if not event.member.is_bot and not event.member.is_system:
        logging.info(f"User: {event.user.username} joined the server")
        result = await auto_verify(str(event.user.username), event.user.id)

        if result == 0:
            await event.app.rest.create_message(server_info['logs'], "Auto verify: The MySQL server is down <@427401640061042689>", user_mentions=True) # Send error in logs channel
            return
        
        flag = result[0]
        ticket_type = result[2]

        if flag is True: # User already registered
            
            message = f"Hello! Thank you for joining the HackNotts Discord server. It appears that your Discord username is already verified on our database, this means you will not be able to send messages in the server for the time being. An organiser will be in contact shortly to resolve this issue :smile:"
            await event.app.rest.create_message(server_info['logs'], f"User: <@{event.user.id}> joined the server but was already verifed?")
            logging.warning(f"User: {event.user.username} joined the server but was already verifed?")
        elif flag is False: # Autoverification worked
            message = f"Hello! This is an automatic notification to say you have been verified as **{ticket_type}** on the HackNotts Discord server and have accompanying roles assigned to you. This is because you entered your Discord username when assigning your ticket. Please have a look around and introduce yourself!"
            await event.app.rest.add_role_to_member(server_info['server_id'], event.user_id, server_info['verified'])   # adds verified role
            await event.app.rest.add_role_to_member(server_info['server_id'], event.user_id, server_info[ticket_type])  # adds the specific role
            if ticket_type == "Donor":
                await event.app.rest.add_role_to_member(server_info["server_id"], event.user_id, server_info["Hacker"]) # adds hacker role if also doner
        elif flag is None: # Just a join
            return

        if flag is not None:
            try:
                user = await event.app.rest.create_dm_channel(event.user_id)
                await user.send(message)
            except hikari.ForbiddenError:
                logging.info(f"Unable to send welcome message to user {event.user.username}")
                await event.app.rest.create_message(server_info['logs'], f"Unable to send welcome message to user <@{event.user.id}>")
        elif result[0] is None:

            await event.app.rest.create_message(server_info['logs'], "Auto verify: The MySQL server is down <@427401640061042689>", user_mentions=True) # Send error in logs channel
    else:
        logging.info(f"Bot: {event.user.username} joined the server")


@plugin.command
@lightbulb.add_checks(lightbulb.human_only)
@lightbulb.option("ticket", "Your 6 character ticket ID \"1234-5\", case insensitive")
@lightbulb.command("verify", "This is used to manually verify yourself", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def verify_command(ctx: lightbulb.SlashContext) -> None:
    if re.search('^[-A-Za-z0-9]+$', ctx.options.ticket) is not None:
        message = await user_verify(ctx.author.username, ctx.author.id, ctx.options.ticket) # Returns the response and flag

        error = None
        if message is None:
            error = "Manual verify: The MySQL server is down <@427401640061042689>"
            message = ("An internal error has occured. Please try again in a few minutes", None)
        elif message[1] == 1: # The verified flag is true
            error = f"The user <@{ctx.author.id}> tried verifying with ticket reference '{ctx.options.ticket.upper()}' but it is already verified"
        elif message[1] == 2: # They used one with a discord username already filled in but isnt verified
            error = f"The user <@{ctx.author.id}> tried verifying with ticket reference '{ctx.options.ticket.upper()}' but the discord usernames did not match"
        elif message[1] == 3: # Discord username is already linked to a ticket (probably a duped ticket)
            error = f"The user <@{ctx.author.id}> tried verifying with ticket reference '{ctx.options.ticket.upper()}' but their discord usernames is already registered to a ticket reference"            

        if error is not None: # Is there an error?
            logging.warning(error)
            #me = await ctx.bot.rest.create_dm_channel(427401640061042689)
            #await me.send(error) # Send me an error via a DM
            
            await ctx.bot.rest.create_message(server_info['logs'], error, user_mentions=True) # Send error in logs channel
        else:
            if message[2] is not None: # Is there a role to assign? if none then that means that the ticket ref was not found
                await ctx.app.rest.add_role_to_member(server_info['server_id'], ctx.user.id, server_info['verified'])    # adds verified role
                await ctx.app.rest.add_role_to_member(server_info['server_id'], ctx.user.id, server_info[message[2]])    # adds specific role to user

                if message[2] == "Donor":
                    await ctx.app.rest.add_role_to_member(server_info["server_id"], ctx.user.id, server_info["Hacker"])  # adds hacker role if also doner

        await ctx.respond(message[0])
    else:
        await ctx.respond("The ticket can only contain letters, numbers and hyphens")


@plugin.command
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR)
@lightbulb.option("username", "The username to be verified", required=True)
@lightbulb.option("identification", "The ID to be verified", required=True)
@lightbulb.command("verify_user", "Autoverify a user", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def verify_user(ctx: lightbulb.SlashContext) -> None:
    result = auto_verify(ctx.options.username, ctx.options.identification)
    await ctx.respond(result)


def load(bot: Bot) -> None:
    bot.add_plugin(plugin)

def unload(bot: Bot) -> None:
    bot.remove_plugin("verify")