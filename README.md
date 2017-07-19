# Discurses
[![PyPI version](https://badge.fury.io/py/discurses.svg)](https://badge.fury.io/py/discurses)  

A CLI for discord, written in python. The name is a combination of discord and curses, as in the terminal interface library. Discurses doesn't use curses, but i originally planned to. It is now built using urwid, a widget library which _can_ use curses as a rendering engine, but discurses works fine without it.

Questions, bug reports, PR's and comments are all very welcome.  

I can be contacted at `topisani@hamsterpoison.com`
![Discurses chat view](https://github.com/topisani/Discurses/raw/master/docs/graphics/img-2016-10-06-142806.png)

## Installation
### Linux
That one is pretty easy:

```shell
$ pip3 install discurses
```
Python 3.5 is required.

### Windows
Start out by following [this](https://wiki.archlinux.org/index.php/Installation_guide) guide.

After that, follow the instructions for linux above

## Authentication
Put the file `example_discurses.yaml` in your `~/.config/` directory, replace the placeholder with your discord token and rename the file to `discurses.yaml`.
You can get the token by visiting [https://discordapp.com/channels/@me](https://discordapp.com/channels/@me), opening the developer tools (<kbd>Ctrl</kbd>+<kbd>shift</kbd>+<kbd>i</kbd> or <kbd>Command</kbd>+<kbd>shift</kbd>+<kbd>i</kbd>) and Click on the `Application` tab, then on the sidebar: `Local Storage` then click the URL from the dropdown and you should see the `token` key followed by your token, copy whats inside the speech marks and put it in your `.yaml` file.

Note: the developer tools Local storage tab must first be enabled in its settings (for firefox users)
[instructions](https://developer.mozilla.org/en-US/docs/Tools/Storage_Inspector)

## Authentification through editing the source
get the token in the way described above, then edit ~/.local/lib/python3.5/site-packages/discurses/discord.py
and edit the async def login(self) to await super().login("YOUR_TOKEN",bot=False)

## Usage 
discurses 2> /dev/null
redirect errors so they dont show up when using the application

## Contributing
First of all, please do, and if you do, feel free to ask me any questions. Also, the issue reports are up for grabs, but id be very happy to be notified before you start work, just so we dont work on the same thing.
