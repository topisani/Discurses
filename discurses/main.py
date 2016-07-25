import asyncio
import concurrent
import concurrent.futures
import curses
import threading
import time
from curses.textpad import Textbox

import discord

import config


scrn = curses.initscr()
curses.noecho()
curses.cbreak()
curses.curs_set(0)
scrn.keypad(True)

m_win = curses.newwin(curses.LINES - 6, curses.COLS - 1, 1, 2)
client = discord.Client(token=config.table['token'])

visible_messages = []
visible_channel = None


def draw_message(m, y, win):
    win.addstr(y, 1, m.timestamp.strftime("%H:%M"))
    win.addstr(y, 8, m.author.name + ": " + m.content)


def draw_messages(win):
    i = 2
    for m in visible_messages[-(win.getmaxyx()[0] - 2):]:
        draw_message(m, i, win)
        i += 1
    win.refresh()


def notify(string):
    scrn.addstr(1, 1, string)
    scrn.refresh()

client_is_ready = False

@client.event
async def on_ready():
    notify("Logged in as %s" % client.user.name)
    global visible_channel
    global client_is_ready
    visible_channel = client.get_channel(config.table['channel'])


@client.event
async def on_message(message):
    if not message.channel.id == config.table['channel']:
        return
    visible_messages.append(message)
    draw_messages(m_win)


def maketextbox(h,
                w,
                y,
                x,
                value="",
                deco=None,
                underlineChr=curses.ACS_HLINE,
                textColorpair=0,
                decoColorpair=0):
    nw = curses.newwin(h, w, y, x)
    txtbox = curses.textpad.Textbox(nw)
    if deco == "frame":
        scrn.attron(decoColorpair)
        curses.textpad.rectangle(scrn, y - 1, x - 1, y + h, x + w)
        scrn.attroff(decoColorpair)
    elif deco == "underline":
        scrn.hline(y + 1, x, underlineChr, w, decoColorpair)

    nw.addstr(0, 0, value, textColorpair)
    nw.attron(textColorpair)
    return txtbox


textbox = maketextbox(
    1, curses.COLS - 3, curses.LINES - 3, 2, "", deco="frame")

is_writing = True


def enter_is_terminate(x):
    if x == 10:
        return 7
    elif x == 27:
        global is_writing
        is_writing = False
        return 7
    else:
        return x


async def send_message(text):
    await client.send_message(visible_channel, text)


async def write_message():
    global is_writing
    is_writing = True
    curses.curs_set(1)
    message = textbox.edit(enter_is_terminate)
    curses.curs_set(0)
    if is_writing:
        await send_message(message)
    else:
        return

exit = False

async def main_loop():
        notify("client_is_ready: " + str(client_is_ready))
        await asyncio.sleep(3)
        if not client_is_ready:
            return
        ch = scrn.getch()
        if ch == ord('q'):
            global exit
            exit = True
            return
        elif ch == ord('t'):
            await write_message()
        else:
            scrn.addstr(scrn.getmaxyx()[0] - 1, 1,
                        "Press q to quit or t to write a message")
            scrn.refresh()


async def main_task():
    await client.login(config.table['token'], bot=False)
    await client.connect()


loop = asyncio.get_event_loop()

def run_discord_client():
    try:
        loop.run_until_complete(main_task())
    except:
        loop.run_until_complete(client.logout())
    finally:
        loop.close()
        curses.nocbreak()
        scrn.keypad(False)
        curses.echo()
        curses.endwin()


run_discord_client

while True:
    if exit:
        notify("Quitting")
        client.logout()
        loop.close()
        loop.stop()
        curses.nocbreak()
        scrn.keypad(False)
        curses.echo()
        curses.endwin()
        break
