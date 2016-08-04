import yaml
import os

CONFIG_FILE_PATH = os.path.join(
    os.path.expanduser("~"), ".config", "discurses.yaml")
CACHE_DIR_PATH = os.path.join(os.path.expanduser("~"), ".cache", "discurses")
CACHE_AVATARS_PATH = os.path.join(CACHE_DIR_PATH, "avatars")

with open(CONFIG_FILE_PATH, 'r') as file:
    table = yaml.load(file)


async def send_notification(discord, message):
    """
    Send a system notification
    This will be called depending on the current notification settings
    """
    avatar = await discord.get_avatar(message.author)
    os.system(
        "notify-send -i {avatar} \"{author} in {server}#{channel}: {content}\"".format(
            avatar=avatar,
            author=message.author,
            server=message.server,
            channel=message.channel,
            content=message.content))
