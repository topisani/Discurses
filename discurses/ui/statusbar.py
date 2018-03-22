import urwid

import logging
import datetime

from discurses import (keymaps, processing)

logger = logging.getLogger(__name__)


class Statusbar(urwid.WidgetWrap):

    def __init__(self, chat_widget):
        self.chat = chat_widget
        self.ui = self.chat.ui
        self.discord = self.chat.discord

        # Public widgets
        self.w_echo = urwid.Text('')
        self.w_typing = TypingList(self.chat)

        # Setup layout
        self._w_layout = urwid.AttrMap(
            urwid.Padding(
                urwid.Columns([('pack', self.w_echo),
                               ('weight', 1, self.w_typing)]),
                left=1, right=1),
            'statusbar')
        self.__super.__init__(self._w_layout)

    def echo(self, message, *args, **kwargs):
        logger.info('Echo: ' + message, *args, **kwargs)
        self.w_echo.set_text(message.format(*args, **kwargs))


class TypingList(urwid.WidgetWrap):
    def __init__(self, chat_widget):
        self.chat = chat_widget
        self.typing = {}
        self.w_txt = urwid.Text("", align="right")
        self.chat.discord.add_event_handler("on_typing", self.on_typing)
        self.chat.discord.add_event_handler("on_message", self.on_message)
        self.update_typing()
        self.__super.__init__(urwid.AttrMap(self.w_txt, "statusbar_typing"))

    def on_typing(self, channel, user, when):
        if channel in self.chat.channels:
            self.typing[user.id] = {'when': datetime.datetime.utcnow(),
                                    'user': user,
                                    'channel': channel}

    def on_message(self, message):
        if message.author.id in self.typing.keys():
            del self.typing[message.author.id]

    def update_typing(self, loop=None, loopDat=None):
        if loop is None:
            loop = self.chat.ui.urwid_loop
        now = datetime.datetime.utcnow()
        time = now - datetime.timedelta(0, 10, 0)
        users = []
        rm = []
        for typ in self.typing.values():
            if typ['when'] < time:
                rm.append(typ['user'].id)
                continue
            users.append(typ['user'].display_name)
        for r in rm:
            del self.typing[r]
        if len(users) > 0:
            self.w_txt.set_text("Typing: " + str.join(", ", users))
        else:
            self.w_txt.set_text("")
        loop.set_alarm_in(0.2, self.update_typing)


