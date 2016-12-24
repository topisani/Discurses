import discurses.discord
import sys
import logging
import discurses.log

def exc_handler(type, value, tb):
    logging.getLogger('discurses').exception("Uncaught exception: {0}".format(str(value)))

sys.excepthook = exc_handler

def main():
    client = discurses.discord.DiscordClient()
    client.run()
