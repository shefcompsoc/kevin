import lightbulb, logging, asyncio, json, mysql.connector

from HackNottsVerification.bot import Bot

server_info = {
    'server_id': 1147945134831440082,
    'here_role': 1147945134831440084,
    'logs': 1150024069161435216
}

plugin = lightbulb.Plugin("here", default_enabled_guilds=server_info['server_id'])

HOST = 'localhost'
PORTS = (5003, 5004, 5005, 5006)

@plugin.command
@lightbulb.command("here", "Use this to manually get the 'I was here' role!", auto_defer = True, ephemeral = True)
@lightbulb.implements(lightbulb.SlashCommand)
async def here(ctx: lightbulb.SlashContext):
    role_id = server_info['here_role']
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
        await ctx.app.rest.create_message(server_info['logs'], f"<@{ctx.user.id}> used `/here` but is not in the database")
        return
    db.close()

    if result['CheckedIn'] == 0:
        await ctx.respond("You have not checked in yet!")
    elif result['CheckedIn'] == 1:
        await plugin.bot.rest.add_role_to_member(ctx.guild_id, ctx.user.id, role_id)
        logging.info(f"User: {ctx.user.username} checked in")
        await ctx.respond("*You're in*")
    else:
        ctx.respond("An error occured! Please try again later :smiley:")
        await ctx.app.rest.create_message(server_info['logs'], f"<@{ctx.user.id}> used `/here` but had an error?")

# Checkin port from checkin server
async def handle_client(reader, writer):
    logging.debug("Connection made")
    data = await reader.read(100)           # Read incomming stream
    message = json.loads(data.decode())     # Decode it

    await plugin.app.rest.add_role_to_member(server_info['server_id'], message['user'], server_info['here_role']) # Add the role
    logging.info(f"User: {await plugin.app.rest.fetch_user(message['user'])} checked in")
    
    writer.write(bytes(json.dumps({"status": "done"}), "utf-8")) # Let the other end know you are done
    await writer.drain()

    logging.debug("Close the connection") # Only needs to do one thing so close the conn
    writer.close()
    await writer.wait_closed()

async def run_server():
    try:
        for i in PORTS:
            server = await asyncio.start_server(handle_client, 'localhost', i)
            logging.info(f"Here server open on port: {i}")
            break
    except OSError:
        pass

    async with server:
        await server.serve_forever()

socket = asyncio.create_task(run_server())

def load(bot: Bot) -> None:
    bot.add_plugin(plugin)

def unload(bot: Bot) -> None:
    socket.cancel() # Stop the thing from continuing and blocking the port
    bot.remove_plugin("here")
