"""
Everything UI
"""
import asyncio
import curses
import main

loop = None
stdscreen = None

def key_loop(stdscreen):
    KEYS_QUIT = (ord('q'))
    KEYS_TYPE = (ord('t'))

    while True:
        stdscreen.noutrefresh()

        c = stdscreen.getch()

        if c in KEYS_TYPE: pass  #TODO fixthat
        if c in KEYS_QUIT: pass  #TODO fixthattoo


def init():
    global stdscreen
    stdscreen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)


def end():
    curses.echo()
    curses.nocbreak()
    curses.curs_set(1)
    curses.endwin()


def notify(string):
    stdscreen.addstr(1, curses.COLS - len(string) - 2, string)
    stdscreen.refresh()


class ChannelView:

    current = None

    def __init__(self, channels=[], messages=[]):
        self.channels = channels
        self.messages = messages

    def display(self):
        L = curses.LINES
        C = curses.COLS
        self.message_win = curses.newwin(L-4, C-1, 0, 1)
        self.message_win.refresh()
        stdscreen.refresh()
        ChannelView.current = self

    def __draw_message(self, m, y):
        self.message_win.addstr(y, 1, m.timestamp.strftime("%H:%M"))
        self.message_win.addstr(y, 8, m.author.name + ": " + m.content)

    def draw_messages(self):
        i = 0
        self.message_win.clear()
        for m in self.messages[-(self.message_win.getmaxyx()[0] - 1):]:
            self.__draw_message(m, i)
            i += 1
        self.message_win.refresh()

    def on_message(self, message):
        self.messages.append(message)
        self.draw_messages()

