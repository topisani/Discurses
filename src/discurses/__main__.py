from . import discord
from . import log  # noqa


def main():
    """Run discurses."""
    client = discord.DiscordClient()
    client.run()

if __name__ == '__main__':
    discurses.main()
