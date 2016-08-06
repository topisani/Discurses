import os
import re
import urwid

import discurses.config
import discurses.processing
from discurses.ui import (MessageEditWidget, MessageListWidget,
                          SendChannelSelector, ServerTree)
from discurses.ui.lib import TextEditWidget


class ChatWidget(urwid.WidgetWrap):
    """This widget holds:
        1. A MessageListWidget of all the messages in channels
        2. A EditMessageWidget, sending messages to send_channel
    """

    def __init__(self, discord_client, channels, send_channel, name=""):
        self.discord = discord_client
        self.ui = self.discord.ui
        self.channels = channels
        self.send_channel = send_channel
        self.name = name
        self._selectable = False
        self.channel_names = discurses.processing.shorten_channel_names(
            channels, 14)
        self.w_channel_cols = SendChannelSelector(self)
        self.message_list = MessageListWidget(self.discord, self)
        self.edit_message = MessageEditWidget(self.discord, self)
        self.frame = urwid.Pile([('weight', 1, self.message_list),
                                 ('pack', self.edit_message)], 1)
        self.pop_up = urwid.Frame(urwid.WidgetPlaceholder(None))
        self.pop_up_overlay = urwid.Overlay(
            urwid.LineBox(self.pop_up), self.frame, 'center', ('relative', 60),
            'middle', ('relative', 60))
        self.w_placeholder = urwid.WidgetPlaceholder(self.frame)
        self.__super.__init__(self.w_placeholder)
        if len(channels) == 0:
            self.open_pop_up(ServerTree(self))

    def keypress(self, size, key):
        key = self._w.keypress(size, key)
        if key == None:
            return
        if key in ("s", "meta s"):
            self.open_pop_up(ServerTree(self))
            return
        if key in ("ctrl l", ):
            self.channel_list_updated()
        if key == "up":
            if self.frame.focus_position > 0:
                self.frame.focus_position -= 1
                return
        if key == "down":
            if self.frame.focus_position < len(self.frame.widget_list) - 1:
                self.frame.focus_position += 1
                return
        if re.match("meta [0-9]", key):
            return self.ui._keypress(key)
        if key in ("n", "ctrl n", "meta n"):

            def _callback(txt):
                if txt is not None:
                    self.set_name(txt)
                self.close_pop_up()

            self.open_text_prompt(_callback, "Change tab name", self.name)
        if key in ("meta c", ):

            def _callback(txt):
                if txt is not None:
                    self.edit_message.edit.insert_text("```\n" + os.popen(
                        txt).read() + "\n```")
                self.close_pop_up()

            self.open_text_prompt(_callback, "Send results of command")
        if key in ("meta f", ):

            def _callback(path):
                def _callback2(txt):
                    self.close_pop_up()
                    self.discord.async(
                        self.discord.send_file(
                            destination=self.send_channel,
                            fp=path,
                            content=txt))

                self.open_text_prompt(_callback2, "Message contents",
                                      self.edit_message.edit.edit_text)

            discurses.config.file_picker(_callback, self)

        return key

    def set_name(self, string):
        self.name = string
        self.ui.w_tabs.update_columns()

    def channel_list_updated(self, get_logs=True):
        self.channel_names = discurses.processing.shorten_channel_names(
            self.channels, 14)
        if get_logs:
            self.message_list.list_walker.invalidate()
        self.message_list.w_sidebar.update_list()
        self.w_channel_cols.update_columns()
        self.edit_message.update_text()

    def open_pop_up(self,
                    widget,
                    header=None,
                    footer=None,
                    height=('relative', 60),
                    width=('relative', 60)):
        self.pop_up.body.original_widget = widget
        self.pop_up.header = header
        self.pop_up.footer = footer
        self.pop_up_overlay.set_overlay_parameters('center', width, 'middle',
                                                   height)
        self.w_placeholder.original_widget = self.pop_up_overlay

    def open_text_prompt(self, callback, title="", content=""):
        self.open_pop_up(
            urwid.Filler(TextEditWidget(
                callback, content=content)),
            header=urwid.Text(
                title, align='center'),
            height=6,
            width=50)

    def close_pop_up(self):
        self.pop_up.body.original_widget = None
        self.pop_up.header = None
        self.pop_up.footer = None
        self.pop_up_overlay.set_overlay_parameters('center', ('relative', 60),
                                                   'middle', ('relative', 60))
        self.w_placeholder.original_widget = self.frame
