import asyncio
import concurrent
import concurrent.futures
import curses
import time
import threading
from curses.textpad import Textbox

import discord

import config
import ui

client = discord.Client(token=config.table['token'])
client_is_ready = False


@client.event
async def on_ready():
    ui.notify("Logged in as %s" % client.user.name)
    channel_view = ui.ChannelView(channels=[client.get_channel(config.table['channel'])])
    channel_view.display()

async def main_task():
    await client.login(config.table['token'], bot=False)
    await client.connect()

loop = asyncio.get_event_loop()

@client.event
async def on_message(m):
    ui.ChannelView.current.on_message(m)

def run_discord_client():
    try:
        loop.run_until_complete(main_task())
    except:
        loop.run_until_complete(client.logout())
    finally:
        loop.close()
        ui.end()


def main():
    ui.init()
    run_discord_client()

if __name__ == '__main__':
    main()
