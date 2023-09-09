import hikari, lightbulb, logging, asyncio, json

from HackNottsVerification.bot import Bot

plugin = lightbulb.Plugin("here", default_enabled_guilds=1147945134831440082)

HOST = 'localhost'
PORTS = (5003, 5004, 5005, 5006)

async def handle_client(reader, writer):
    logging.debug("Connection made")
    data = await reader.read(100)           # Read incomming stream
    message = json.loads(data.decode())     # Decode it

    await plugin.app.rest.add_role_to_member(1147945134831440082, message['user'], 1147945134831440084) # Add the role
    logging.info(f"Checked in user: {message['user']}")
    
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
