import yaml
import os
import shlex

CONFIG_FILE_PATH = os.path.join(
    os.path.expanduser("~"), ".config", "discurses.yaml")
CACHE_DIR_PATH = os.path.join(os.path.expanduser("~"), ".cache", "discurses")
CACHE_AVATARS_PATH = os.path.join(CACHE_DIR_PATH, "avatars")

with open(CONFIG_FILE_PATH, 'r') as file:
    table = yaml.load(file)


def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

create_dir(CACHE_AVATARS_PATH)

async def send_notification(discord, message):
    """
    Send a system notification
    This will be called depending on the current notification settings
    """
    avatar = await discord.get_avatar(message.author)
    nickname = message.author.display_name
    os.system(
        "notify-send -i {avatar} \"{author} in {server}#{channel}\" {content}"
        .format(
            avatar=shlex.quote(avatar),
            author=shlex.quote(nickname),
            server=shlex.quote(message.server.name),
            channel=shlex.quote(message.channel.name),
            content=shlex.quote(message.clean_content)))


def file_picker(callback, chat_widget):
    """
    Open some sort of file picker
    This default implementation opens a text prompt

    The callback takes one argument, the file path

    chat_widget is the instance of ChatWidget.
    """

    def _callback2(txt):
        if txt is not None:
            path = os.path.expanduser(txt)
            if os.path.isfile(path):
                callback(path)
            else:
                chat_widget.open_text_prompt(_callback2, "File not found",
                                             path)
        else:
            chat_widget.close_pop_up()

    chat_widget.open_text_prompt(_callback2, "Send File")


def to_clipboard(text):
    os.system("echo {} | xclip -selection c".format(shlex.quote(text)))
