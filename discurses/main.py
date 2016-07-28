import asyncio

import discord

import config
import ui

client = discord.Client(token=config.table['token'], bot=False)
client_is_ready = False
loop = asyncio.get_event_loop()

event_handlers = {"on_message": []}


@client.event
async def on_ready():
    ui.notify("Logged in as %s" % client.user.name)
    ui.on_ready()


@client.event
async def on_message(m):
    ui.notify("Event handlers for on_message: %d" % len(event_handlers['on_message'])) 
    for f in event_handlers['on_message']:
        ui.notify("called event handler for on_message")
        ui.loop(0.1, f, m)


async def main_task():
    await client.login(config.table['token'], bot=False)
    await client.connect()


def send_message(channel, message):
    client.loop.create_task(client.send_message(channel, message))


def get_logs(channel):
    return []


async def get_those_logs(channel):
    messages = []
    async for message in client.logs_from(channel):
        messages.append(message)
    return messages


def run_discord_client():
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main_task())
    except:
        loop.run_until_complete(client.logout())
    finally:
        loop.close()


def main():
    ui.init()
    run_discord_client()


if __name__ == '__main__':
    main()
