import enum
import os

import urwid

import discurses.config
import discurses.keymaps as keymaps
import discurses.processing
from discurses.ui import (HasModal, MessageEditWidget, MessageListWidget,
                          SendChannelSelector, ServerTree, Statusbar)

from discurses.ui.member_list import MemberList


class ChatWindow(urwid.WidgetWrap, HasModal):
    """
    A chat window holds:
    - A message list
    - Sidebars
    - A Statusbar
    - An EditMessageWidget
    """

    class FocusTarget(enum.Enum):
        CHANNEL_SELECTOR = enum.auto()
        MESSAGE_LIST = enum.auto()
        MESSAGE_EDIT = enum.auto()
        MEMBER_LIST = enum.auto()
        SERVER_TREE = enum.auto()
        STATUSBAR = enum.auto()

    def __init__(self, discord_client, channels, send_channel, name):
        self.discord = discord_client
        self.channels = channels
        self.send_channel = send_channel
        self.ui = self.discord.ui
        self.channel_names = discurses.processing \
            .shorten_channel_names(channels, 14)
        self.name = name

        # Public widgets
        self.w_channel_selector = SendChannelSelector(self)
        self.w_message_list = MessageListWidget(self.discord, self)
        self.w_message_edit = MessageEditWidget(self.discord, self)
        self.w_member_list = MemberList(self)
        self.w_server_tree = ServerTree(self)
        self.w_statusbar = Statusbar(self)

        # Public fields
        self.show_member_list = True
        self.show_server_tree = True

        # Setup layout widgets
        self._setup_layout()
        HasModal.__init__(self, self._w_layout)
        urwid.WidgetWrap.__init__(self, self._w_placeholder)
        self.set_focus(ChatWindow.FocusTarget.SERVER_TREE)

    def _setup_layout(self):
        """
        Called from __init__
        """
        self._w_columns = urwid.Columns([])
        self._w_pile = urwid.Pile(
            [('weight', 1, self._w_columns),
             ('pack', self.w_statusbar),
             ('pack', self.w_message_edit),
             ])

        self._w_layout = self._w_pile
        self._w_server_tree_column = urwid.LineBox(
                    self.w_server_tree,
                    tlcorner='', tline='',
                    lline='', trcorner='│',
                    blcorner='', rline='│',
                    bline='', brcorner='│')
        self._w_member_list_column = urwid.LineBox(
                    self.w_member_list,
                    tlcorner='│', tline='',
                    lline='│', trcorner='',
                    blcorner='│', rline='',
                    bline='', brcorner='')
        self._refresh_layout()

    def _refresh_layout(self):
        """
        Refresh sidebar visibility changes
        """
        focus_before = self._w_columns.get_focus()
        columns = []
        if self.show_server_tree:
            columns.append((self._w_server_tree_column,
                            self._w_columns.options('weight', 0.25)))

        columns.append((self.w_message_list,
                        self._w_columns.options('weight', 1)))

        if self.show_member_list:
            columns.append((self._w_member_list_column,
                            self._w_columns.options('weight', 0.25)))

        self._w_columns.contents = columns
        if focus_before is not None:
            self._w_columns.set_focus(focus_before)
        else:
            self._w_columns.focus_position = 0

    @keymaps.CHAT.keypress
    def keypress(self, size, key):
        """Forward keypresses to the wrapped widget"""
        return self._w.keypress(size, key)

    @keymaps.GLOBAL.command
    def redraw(self):
        self.channel_list_updated()

    @keymaps.CHAT.command
    def focus_up(self):
        if self._w_pile.focus_position > 0:
            self._w_pile.focus_position -= 1

    @keymaps.CHAT.command
    def focus_down(self):
        if self._w_pile.focus_position < len(self._w_pile.widget_list) - 1:
            self._w_pile.focus_position += 1
            return

    @keymaps.CHAT.command
    def set_focus(self, target):
        if type(target) is str:
            target = ChatWindow.FocusTarget[target]
        if type(target) is ChatWindow.FocusTarget:
            if target == ChatWindow.FocusTarget.CHANNEL_SELECTOR:
                self._w_layout.set_focus(self.w_channel_selector)
            elif target == ChatWindow.FocusTarget.MESSAGE_EDIT:
                self._w_layout.set_focus(self.w_message_edit)
            elif target == ChatWindow.FocusTarget.STATUSBAR:
                self._w_layout.set_focus(self.w_statusbar)
            elif target == ChatWindow.FocusTarget.MESSAGE_LIST:
                self._w_layout.set_focus(self._w_columns)
                self._w_columns.set_focus(self.w_message_list)
            elif target == ChatWindow.FocusTarget.MEMBER_LIST:
                self._w_layout.set_focus(self._w_columns)
                self._w_columns.set_focus(self._w_member_list_column)
            elif target == ChatWindow.FocusTarget.SERVER_TREE:
                self._w_layout.set_focus(self._w_columns)
                self._w_columns.set_focus(self._w_server_tree_column)

    @keymaps.CHAT.command
    def ask_rename_tab(self):
        def _callback(txt):
            if txt is not None:
                self.set_name(txt)
            self.close_pop_up()

        self.open_text_prompt(_callback, "Change tab name", self.name)

    @keymaps.CHAT.command
    def ask_shell_command(self):
        def _callback(txt):
            if txt is not None:
                self.edit_message.edit.insert_text("```\n" + os.popen(
                    txt).read() + "\n```")
            self.close_pop_up()

        self.open_text_prompt(_callback, "Send results of command")

    @keymaps.CHAT.command
    def ask_send_file(self):
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
        self.w_message_list.list_walker.invalidate()

    @keymaps.CHAT.command
    def toggle_server_list(self, flag=None):
        """Toggle the left sidebar"""
        if flag is None:
            flag = not self.show_server_tree
        self.show_server_tree = flag
        self._refresh_layout()
        if flag:
            self.set_focus(ChatWindow.FocusTarget.SERVER_TREE)

    @keymaps.CHAT.command
    def toggle_member_list(self, flag=None):
        """Toggle the right sidebar"""
        if flag is None:
            flag = not self.show_member_list
        self.show_member_list = flag
        self._refresh_layout()
        if flag:
            self.set_focus(ChatWindow.FocusTarget.MEMBER_LIST)

    def channel_list_updated(self, get_logs=True):
        self.channel_names = discurses.processing.shorten_channel_names(
            self.channels, 14)
        if get_logs:
            self.refetch_messages()
        self.w_member_list.update_list()
        self.w_channel_selector.update_columns()
        self.w_message_edit.update_text()

    def set_send_channel(self, channel):
        self.send_channel = channel
        self.w_message_list.update_all_columns()
        self.w_channel_selector.update_columns()
        self.w_message_edit.update_text()

    def set_name(self, name):
        self.name = name
