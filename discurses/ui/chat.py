import os
import re

import urwid

import discurses.config
import discurses.keymaps as keymaps
import discurses.processing
from discurses.ui import (HasModal, MessageEditWidget, MessageListWidget,
                          SendChannelSelector, ServerTree)
from discurses.ui.lib import TextEditWidget


class ChatWidget(urwid.WidgetWrap, HasModal):
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
        HasModal.__init__(self, self.frame)
        self.__super.__init__(self.w_placeholder)
        if len(channels) == 0:
            self.popup_server_tree()

    @keymaps.CHAT.keypress
    def keypress(self, size, key):
        return self._w.keypress(size, key)

    @keymaps.CHAT.command
    def popup_server_tree(self):
        def cb():
            self.close_pop_up()
        self.open_pop_up(ServerTree(self, close_callback=cb))

    @keymaps.GLOBAL.command
    def redraw(self):
        self.channel_list_updated()

    @keymaps.CHAT.command
    def focus_up(self):
        if self.frame.focus_position > 0:
            self.frame.focus_position -= 1

    @keymaps.CHAT.command
    def focus_down(self):
        if self.frame.focus_position < len(self.frame.widget_list) - 1:
            self.frame.focus_position += 1
            return

    @keymaps.CHAT.command
    def popup_rename_tab(self):
        def _callback(txt):
            if txt is not None:
                self.set_name(txt)
            self.close_pop_up()

        self.open_text_prompt(_callback, "Change tab name", self.name)

    @keymaps.CHAT.command
    def popup_shell_command(self):
        def _callback(txt):
            if txt is not None:
                self.edit_message.edit.insert_text("```\n" + os.popen(
                    txt).read() + "\n```")
            self.close_pop_up()

        self.open_text_prompt(_callback, "Send results of command")

    @keymaps.CHAT.command
    def popup_send_file(self):
        def _callback(path):
            def _callback2(txt):
                self.close_pop_up()
                self.discord.async(
                    self.discord.send_file(
                        destination=self.send_channel, fp=path, content=txt))

            self.open_text_prompt(_callback2, "Message contents",
                                  self.edit_message.edit.edit_text)

        discurses.config.file_picker(_callback, self)

    @keymaps.CHAT.command
    def refetch_messages(self):
        self.message_list.list_walker.invalidate()

    def set_name(self, string):
        self.name = string
        self.ui.w_tabs.update_columns()

    def channel_list_updated(self, get_logs=True):
        self.channel_names = discurses.processing.shorten_channel_names(
            self.channels, 14)
        if get_logs:
            self.refetch_messages()
        self.message_list.w_sidebar.update_list()
        self.w_channel_cols.update_columns()
        self.edit_message.update_text()

    def set_send_channel(self, channel):
        self.send_channel = channel
        self.message_list.update_all_columns()
        self.w_channel_cols.update_columns()
        self.edit_message.update_text()
