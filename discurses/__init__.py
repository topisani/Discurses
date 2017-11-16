from . import discord
from . import log  # noqa


def main():
    client = discord.DiscordClient()
    client.run()
