import logging
import discurses.discord

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)

def main():
    client = discurses.discord.DiscordClient()
    client.run()
