import os
import shlex
import platform
import subprocess
import yaml

CONFIG_FILE_PATH = os.path.join(
    os.path.expanduser("~"), ".config", "discurses.yaml")
CACHE_DIR_PATH = os.path.join(os.path.expanduser("~"), ".cache", "discurses")
CACHE_AVATARS_PATH = os.path.join(CACHE_DIR_PATH, "avatars")

PLATFORM = platform.system()

try:
    with open(CONFIG_FILE_PATH, 'r') as file:
        table = yaml.load(file)
except FileNotFoundError:
    print(
        "Create an authentication configuration file {path}"
        .format(
            path=shlex.quote(CONFIG_FILE_PATH)))
    raise


def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

create_dir(CACHE_AVATARS_PATH)

def macos_notify(message, nickname):
    """
    Create a MacOS notification
    Snippet from:
    https://stackoverflow.com/questions/17651017/python-post-osx-notification/41318195#41318195
    """
    subprocess.Popen(['osascript', "-e 'display notification '{}' with title '{}''"
                      .format(shlex.quote(nickname), shlex.quote(message.clean_content))])

def linux_notify(message, avatar, nickname):
    """
    Create a linux notification
    """
    if message.channel.is_private:
        subprocess.Popen(["notify-send", "-i {avatar} \"{author} in chat with {users}:\" {content}"
                          .format(
                              avatar=shlex.quote(avatar),
                              author=shlex.quote(nickname),
                              content=shlex.quote(message.clean_content),
                              users=shlex.quote(', '
                                                .join(a.display_name for a in message.channel.recipients)))])
    else: 
        quoteAvatar = "{avatar}".format(avatar=avatar)
        quoteFrom = "{author} in {server}#{channel}".format(
                author=nickname,
                server=message.server.name,
                channel=message.channel.name)
        quoteMessage = "{content}".format(content=message.clean_content)
        quoteAvatar = shlex.quote(quoteAvatar)
        quoteFrom = shlex.quote(quoteFrom)
        quoteMessage = shlex.quote(quoteMessage)
        shellCmd = "notify-send -i {a} {b} {c}".format(a=quoteAvatar, b=quoteFrom, c=quoteMessage)
        subprocess.Popen(shellCmd, shell=True)

async def send_notification(discord, message):
    """
    Send a system notification
    This will be called depending on the current notification settings
    """
    avatar = await discord.get_avatar(message.author)
    nickname = message.author.display_name
    if PLATFORM == "Linux":
        linux_notify(message, avatar, nickname)
    elif PLATFORM == "Darwin":
        macos_notify(message, nickname)

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
