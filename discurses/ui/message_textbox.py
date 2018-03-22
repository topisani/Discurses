import datetime

import urwid

import discurses.processing as processing
import discurses.keymaps as keymaps


class MessageEditWidget(urwid.WidgetWrap):
    """Wrapper for Edit widget, mainly to allow capturing keypresses"""

    def __init__(self, discord_client, chat_widget):
        self.discord = discord_client
        self.ui = self.discord.ui
        self.chat_widget = chat_widget
        self.editing = None
        self.edit = urwid.Edit(multiline=True, allow_tab=True)
        self.edit.keypress = self._edit_keypress
        self.w_channel = urwid.Text("")
        self.w_edit_line = urwid.Columns([
            ('pack', self.w_channel),
            ('weight', 1, urwid.Padding(self.edit, left=1, right=1))
        ])
        self.pile = urwid.Pile([])
        self.hide_channel_selector()
        self.__super.__init__(self.pile)

    def selectable(self):
        # This is where we can disable the edit widget
        # if the user is missing permissions
        return True

    def set_channel_name(self, str):
        self.w_channel.set_text("[{}]".format(str))

    @keymaps.MESSAGE_TEXT_BOX.command
    def send_message(self):
        if self.edit.edit_text == "":
            self.cancel_edit()
            return
        if self.editing is not None:
            self.discord.async(
                self.discord.edit_message(self.editing, self.edit.edit_text))
            self.cancel_edit()
        else:
            self.discord.async(
                self.discord.send_message(self.chat_widget.send_channel,
                                          self.edit.edit_text))
        self.edit.set_edit_text("")

    @keymaps.MESSAGE_TEXT_BOX.keypress
    def keypress(self, size, key):
        return self.pile.focus_item.keypress(size, key)

    @keymaps.MESSAGE_TEXT_BOX.command
    def focus_message_list(self):
        self.chat_widget.w_message_list.scroll_to_bottom()
        self.chat_widget.set_focus('MESSAGE_LIST')

    @keymaps.MESSAGE_TEXT_BOX.command
    def insert(self, text):
        self.edit.insert_text(text)

    def _edit_keypress(self, size, key):
        if key == "enter":
            return key
        key = urwid.Edit.keypress(self.edit, size, key)
        if key is None:
            if self.editing is None:
                self.discord.async(
                    self.discord.send_typing(self.chat_widget.send_channel))
        return key

    def edit_message(self, message):
        self.chat_widget.w_statusbar.echo("editing")
        self.editing = message
        self.edit.set_edit_text(message.content)
        self.edit.set_edit_pos(len(self.edit.edit_text))

    def reply_to(self, message):
        self.edit.set_edit_text("> _{0}_\n".format(message.content))
        self.edit.set_edit_pos(len(self.edit.edit_text))

    @keymaps.MESSAGE_TEXT_BOX.command
    def cancel_edit(self):
        self.chat_widget.w_statusbar.clear("editing")
        self.editing = None
        self.edit.set_edit_text("")

    @keymaps.MESSAGE_TEXT_BOX.command
    def show_channel_selector(self):
        self.pile.contents = [
            (self.w_edit_line, self.pile.options()),
            (self.chat_widget.w_channel_selector, self.pile.options())
        ]
        self.pile.set_focus(self.chat_widget.w_channel_selector)

    @keymaps.MESSAGE_TEXT_BOX.command
    def hide_channel_selector(self):
        self.pile.contents = [
            (self.w_edit_line, self.pile.options()),
        ]
        self.pile.set_focus(self.w_edit_line)

    @keymaps.MESSAGE_TEXT_BOX.command
    def update_text(self):
        if self.chat_widget.send_channel is not None:
            self.set_channel_name(processing.channel_name(
                self.chat_widget.send_channel))


class SendChannelSelector(urwid.WidgetWrap):
    def __init__(self, chat_widget):
        self.chat_widget = chat_widget
        self.w_cols = urwid.Columns([])
        self._selectable = True
        self.update_columns()
        self.__super.__init__(self.w_cols)

    def selectable(self):
        return True

    @keymaps.SEND_CHANNEL_SELECTOR.keypress
    def keypress(self, size, key):
        return key

    @keymaps.SEND_CHANNEL_SELECTOR.command
    def focus_left(self):
        self.w_cols.focus_position = (
            self.w_cols.focus_position - 1) % len(self.w_cols.widget_list)

    @keymaps.SEND_CHANNEL_SELECTOR.command
    def focus_right(self):
        self.w_cols.focus_position = (
            self.w_cols.focus_position + 1) % len(self.w_cols.widget_list)

    @keymaps.SEND_CHANNEL_SELECTOR.command
    def select_focused(self):
        self.select_channel(self.w_cols.focus_position)

    @keymaps.SEND_CHANNEL_SELECTOR.command
    def exit(self):
        self.chat_widget.w_message_edit.hide_channel_selector()

    @keymaps.SEND_CHANNEL_SELECTOR.command
    def delete_focused(self):
        del self.chat_widget.channels[self.w_cols.focus_position]
        self.chat_widget.channel_list_updated()

    @keymaps.SEND_CHANNEL_SELECTOR.command
    def select_channel(self, index):
        self.chat_widget.set_send_channel(self.chat_widget.channels[index])

    @keymaps.SEND_CHANNEL_SELECTOR.command
    def update_columns(self):
        cols = []
        names = processing.shorten_channel_names(
            self.chat_widget.channels, 100)
        for ch in self.chat_widget.channels:
            if ch == self.chat_widget.send_channel:
                cols.append((urwid.AttrMap(
                    urwid.Text(
                        names[ch], align="center"),
                    "send_channel_selector_sel",
                    "send_channel_selector_sel_f"),
                             self.w_cols.options('weight', 1)))
            else:
                cols.append((urwid.AttrMap(
                    urwid.Text(
                        names[ch], align="center"),
                    "send_channel_selector",
                    "send_channel_selector_f"),
                             self.w_cols.options('weight', 1)))
        self.w_cols.contents = cols
