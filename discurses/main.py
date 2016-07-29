import asyncio
from typing import List

import discord
from discord import Channel, Message

import config
import ui


class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = ui.MainUI(self)
        self.event_handlers = {
            "on_message": [],
            "on_message_edit": [],
            "on_message_delete": []
        }

    def add_event_handler(self, event: str, f):
        self.event_handlers[event].append(f)

    async def on_ready(self):
        self.ui.notify("Logged in as %s" % self.user.name)
        self.ui.on_ready()

    async def on_message(self, m: Message):
        for f in self.event_handlers['on_message']:
            f(m)

    async def on_message_edit(self, before: Message, after: Message):
        for f in self.event_handlers['on_message_edit']:
            f(before, after)

    async def on_message_delete(self, m: Message):
        for f in self.event_handlers['on_message_delete']:
            f(m)

    async def login(self):
        await super().login(config.table['token'], bot=False)

    def async(self, f):
        self.loop.create_task(f)

    async def get_logs_from(self, channel: Channel) -> List[Message]:
        messages = []
        print("getting logs")
        async for m in self.logs_from(channel, limit=20):
            messages.append(m)
        print("got logs")
        return messages


if __name__ == '__main__':
    client = DiscordClient()
    client.run()
