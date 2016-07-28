"""
Everything UI
"""
import asyncio

import discord
import urwid

import main


palette = [
    ("message", "white", "", "standout"),
    ("time", "dark cyan", "", "standout"),
    ("author", "dark green", "", "standout"),
    ("focus", "dark red", "", "standout"),
    ("dim", "dark cyan", "", "standout"),
    ("head", "light red", "black"),
]

urwid_loop = None
frame = None


def init():
    global urwid_loop
    global frame

    def keystroke(input):
        if input in ("q", "Q"):
            urwid_loop.stop()
            main.client.stop()

    header = urwid.AttrMap(urwid.Text("Loging in", align="center"), "head")
    frame = urwid.Frame(urwid.Filler(urwid.Text("Please stand by")), header=header)
    urwid_loop = urwid.MainLoop(frame,
                          palette=palette,
                          unhandled_input=keystroke,
                          event_loop=urwid.AsyncioEventLoop(loop=main.loop))

    def refresh(_loop, _data):
        _loop.draw_screen()
        _loop.set_alarm_in(2, refresh)

    urwid_loop.set_alarm_in(0.2,refresh)

    notify("UI initialized")
    urwid_loop.start()


def set_body(w):
    frame.set_body(w)
    draw_screen()
    

def notify(string):
    string = str(string)
    frame.set_header(urwid.AttrWrap(urwid.Text(string), "head"))


def draw_screen():
    urwid_loop.draw_screen()


def on_ready():
    channels = []
    for channel in main.client.get_all_channels():
        channels.append(channel)
    set_body(ChatWidget(channels, channels[0]))


class ChatWidget(urwid.WidgetWrap):
    """This widget holds:
        1. A MessageListWidget of all the messages in channels
        2. A EditMessageWidget, sending messages to send_channel
    """
    def __init__(self, channels, send_channel):
        self.channels = channels
        self.send_channel = send_channel
        self._selectable = False

        self.message_list = MessageListWidget(channels)
        self.edit_message = MessageEditWidget(send_channel)
        pile = urwid.Frame(
            self.message_list,
            footer=self.edit_message)
        self.__super.__init__(pile)


class MessageListWidget(urwid.WidgetWrap):
    """The Listbox of MessageWidgets"""

    def __init__(self, channels):
        self.channels = channels
        messages = []
        for channel in channels:
            for message in main.get_logs(channel):
                messages.append(MessageWidget(message))
                
        self.list_walker = urwid.SimpleListWalker(messages)
        self.listbox = urwid.ListBox(self.list_walker)
        main.event_handlers['on_message'].append(self.on_message)
        self.__super.__init__(self.listbox)

    def add_message(self, message):
        self.list_walker.append(MessageWidget(message))
        self.listbox.set_focus(len(self.list_walker) - 1)
        draw_screen()

    def on_message(self, message):
        if message.channel in self.channels:
            self.add_message(message)


class MessageWidget(urwid.WidgetWrap):
    """A view of a message in the MessageListWidget"""
    def __init__(self, m):
        self.content = "%s  %s: %s" % (m.timestamp.strftime("%H:%M"),
                                       m.author.name, m.content)
        self.item = [
            ("fixed", 8, urwid.Padding(
                urwid.AttrWrap(
                    urwid.Text(m.timestamp.strftime("%H:%M")), "time",
                    "focus"),
                left=1)),
            ("fixed", 15, urwid.Padding(
                urwid.AttrWrap(
                    urwid.Text("%s: " % m.author.name), "author", "focus"),
                right=1)),
            urwid.AttrWrap(urwid.Text("%s" % m.content), "message", "focus"),
        ]
        w = urwid.Columns(self.item)
        self.__super.__init__(w)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


class MessageEditWidget(urwid.WidgetWrap):
    """Wrapper for Edit widget, mainly to allow capturing keypresses"""

    def __init__(self, channel):
        self.channel = channel
        w = urwid.Edit()
        self.__super.__init__(w)

    def selectable(self):
        # This is where we can disable the edit widget
        # if the user is missing permissions
        return True

    def keypress(self, size, key):
        if key == "enter":
            main.send_message(self.channel, self._wrapped_widget.edit_text)
        else:
            return self._wrapped_widget.keypress(size, key)
