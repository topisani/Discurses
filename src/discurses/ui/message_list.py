import datetime

import discord
import urwid

import discurses.processing
import discurses.keymaps as keymaps
import logging

logger = logging.getLogger(__name__)


class MessageListWidget(urwid.WidgetWrap):
    """The Listbox of MessageWidgets"""

    def __init__(self, discord_client, chat_widget):
        self.discord = discord_client
        self.ui = self.discord.ui
        self.chat_widget = chat_widget
        self.list_walker = MessageListWalker(self)
        self.listbox = urwid.ListBox(self.list_walker)
        self.discord.add_event_handler('on_message', self._on_message)
        self.discord.add_event_handler('on_message_edit',
                                       self._on_message_edit)
        self.discord.add_event_handler('on_message_delete',
                                       self._on_message_delete)
        self.scroll_to_bottom()
        self.__super.__init__(self.listbox)

    def add_message(self, message):
        self.list_walker.append(
            MessageWidget(self.discord, self.chat_widget, message))
        focus_status, focus = self.list_walker.get_focus()
        if not focus > len(self.list_walker) - 2:
            self.scroll_to_bottom()
        self.discord.ui.draw_screen()

    def _on_message(self, message):
        if len(self.list_walker) == 0:
            return  # No message to handle
        if message.timestamp.date() != \
                self.list_walker[-1].message.timestamp.date():
            self.list_walker.append(
                DatelineWidget(self.chat_widget, message.timestamp.date()))
        if message.channel in self.chat_widget.channels:
            self.add_message(message)

    def _on_message_edit(self, before, after):
        if before.channel in self.chat_widget.channels:
            for mw in self.list_walker:
                if before.id == mw.message.id:
                    index = self.list_walker.index(mw)
                    self.list_walker[index] = MessageWidget(
                        self.discord, self.chat_widget, after)
                    break

    def _on_message_delete(self, m):
        if m.channel in self.chat_widget.channels:
            for mw in self.list_walker:
                if m.id == mw.message.id:
                    self.list_walker.remove(mw)
                    logger.info("Removed message from listview")
                    break

    def scroll_to_bottom(self):
        if len(self.list_walker) > 0:
            self.listbox.set_focus(len(self.list_walker) - 1)

    @keymaps.MESSAGE_LIST.keypress
    def keypress(self, size, key):
        return self._w.keypress(size, key)

    def mouse_event(self, size, event, button, col, row, focus):
        if event == 'mouse press':
            if button == 4:
                return self.listbox.keypress(size, "up") is not None
            if button == 5:
                return self.listbox.keypress(size, "down") is not None
        return self.listbox.mouse_event(size, event, button, col, row, focus)

    @keymaps.MESSAGE_LIST.command
    def update_all_columns(self):
        for mw in self.list_walker:
            mw.update_columns()

    @keymaps.MESSAGE_LIST.command
    def focus_message_textbox(self):
        self.chat_widget.set_focus('MESSAGE_EDIT')


class MessageListWalker(urwid.MonitoredFocusList, urwid.ListWalker):
    def __init__(self, list_widget):
        self.list_widget = list_widget
        self.is_polling = False
        self.top_reached = False
        urwid.MonitoredFocusList.__init__(self, [])
        self.get_logs(callback=list_widget.scroll_to_bottom)

    def get_logs(self, before=None, callback=lambda: None):
        if before is None and len(self) > 0:
            before = self[0].message.timestamp
        if self.is_polling or self.top_reached:
            return
        self.is_polling = True

        async def _callback():
            messages = []
            for channel in self.list_widget.chat_widget.channels:
                try:
                    async for m in self.list_widget.discord.logs_from(
                            channel, before=before):
                        messages.append(
                            MessageWidget(self.list_widget.discord,
                                          self.list_widget.chat_widget, m))
                except discord.errors.Forbidden:
                    messages.append(
                                ForbiddenWidget(self.list_widget.chat_widget))
            if messages == [] and len(
                    self.list_widget.chat_widget.channels) > 0:
                self.top_reached = True
                messages = [TopReachedWidget(self.list_widget.chat_widget)]

            self[0:0] = messages
            self.sort_messages()
            self._modified()
            self.is_polling = False
            callback()

        self.list_widget.discord.async(_callback())

    def sort_messages(self):
        st = []
        dates = []
        for mw in self:
            if mw.message.id in st or isinstance(mw, DatelineWidget):
                self.remove(mw)
            else:
                st.append(mw.message.id)
            if isinstance(mw, MessageWidget):
                if mw.message.timestamp.date() not in dates:
                    dates.append(mw.message.timestamp.date())

        for d in dates:
            self.append(DatelineWidget(self.list_widget.chat_widget, d))
            logger.debug("Added dateline")
        self.sort(key=lambda mw: mw.message.timestamp)

    def invalidate(self):
        self[:] = []
        self.get_logs(callback=self.list_widget.scroll_to_bottom)

    def _modified(self):
        if self.focus is not None:
            if self.focus >= len(self):
                self.focus = max(0, len(self) - 1)
        urwid.ListWalker._modified(self)

    def set_modified_callback(self, callback):
        """
        This function inherited from MonitoredList is not
        implemented in SimpleFocusListWalker.

        Use connect_signal(list_walker, "modified", ...) instead.
        """
        raise NotImplementedError('Use connect_signal('
                                  'list_walker, "modified", ...) instead.')

    def set_focus(self, position):
        """Set focus position."""
        try:
            if position < 0:
                self.get_logs()
                return
            if position >= len(self):
                raise ValueError
        except (TypeError, ValueError):
            raise IndexError("No widget at position %s" % (position, ))
        self.focus = position
        self._modified()

    def next_position(self, position):
        """
        Return position after start_from.
        """
        if len(self) - 1 <= position:
            raise IndexError
        return position + 1

    def prev_position(self, position):
        """
        Return position before start_from.
        """
        if position <= 0:
            self.get_logs()
            raise IndexError
        return position - 1

    def positions(self, reverse=False):
        """
        Optional method for returning an iterable of positions.
        """
        if reverse:
            return range(len(self) - 1, -1, -1)
        return range(len(self))


class MessageWidget(urwid.WidgetWrap):
    """A view of a message in the MessageListWidget"""

    def __init__(self, discord_client, chat_widget, m):
        self.discord = discord_client
        self.ui = self.discord.ui
        self.chat_widget = chat_widget
        self.message = m
        self.processed = discurses.processing.format_incomming(
            m, self.chat_widget)
        for at in m.attachments:
            self.processed += "\n" + at.get('url')
        self.columns_w = urwid.Columns([])
        w = urwid.AttrMap(self.columns_w, None, discurses.ui.MainUI.focus_attr)
        self.update_columns()
        self.__super.__init__(w)

    @keymaps.MESSAGE_LIST_ITEM.keypress
    def keypress(self, size, key):
        return key

    @keymaps.MESSAGE_LIST_ITEM.command
    def update_columns(self):
        channel_visible = len(self.chat_widget.channels) > 1
        channel_name = self.chat_widget.channel_names[self.message.channel]
        channel_width = min(len(channel_name) + 1, 20)
        author_nickname = self.message.author.display_name
        author_width_extra = 1 if \
            len(author_nickname.encode("utf-8")) > len(author_nickname) else 0
        author_width = 30 - channel_width + author_width_extra
        channel_attr_map = "message_channel" \
            if len(self.chat_widget.channels) > 1 and \
            self.message.channel == self.chat_widget.send_channel \
            else "message_channel_cur"
        self.columns = [
            self.Column(
                'timestamp',
                True, ('given', 7),
                self.message.timestamp.replace(
                    tzinfo=datetime.timezone.utc).astimezone(
                        tz=None).strftime("%H:%M"),
                attr_map="message_timestamp",
                padding=(1, 1)
            ),
            self.Column(
                'channel',
                channel_visible, ('given', channel_width),
                channel_name[:channel_width - 1],
                attr_map=channel_attr_map,
                padding=(0, 1)
            ),
            self.Column(
                'author',
                True, ('given', author_width),
                "{0}:".format(author_nickname.encode("utf-8")[:author_width - 2].
                              decode("utf-8", "ignore")),
                attr_map="message_author",
                padding=(0, 1),
                align="right"
            ),
            self.Column(
                'content',
                True, ('weight', 1),
                self.processed,
                attr_map="message_content",
                padding=(0, 1)
            )
        ]
        visible_cols = []
        for col in self.columns:
            if col.visible:
                visible_cols.append(col)
                self.columns_w.contents = [(c.get_widget(),
                                            self.columns_w.options(
                                                width_type=c.width[0],
                                                width_amount=c.width[1]))
                                           for c in visible_cols]

    def selectable(self) -> bool:
        return True

    @keymaps.MESSAGE_LIST_ITEM.command
    def edit_message(self):
        self.chat_widget.w_message_edit.edit_message(self.message)
        self.chat_widget.set_focus('MESSAGE_EDIT')

    @keymaps.MESSAGE_LIST_ITEM.command
    def delete_message(self):
        if self.message.author == self.discord.user or \
                self.message.channel.permissions_for(self.discord.user).\
                manage_messages:
            self.discord.async(self.discord.delete_message(self.message))

    @keymaps.MESSAGE_LIST_ITEM.command
    def ask_delete_message(self):
        def callback(bool):
            if bool:
                self.delete_message()
        self.chat_widget.open_confirm_prompt(
            callback, "Delete message?",
            [self.message.author.display_name + ":\n   ",
             discurses.processing.format_incomming(self.message,
                                                   self.chat_widget)])

    @keymaps.MESSAGE_LIST_ITEM.command
    def quote_message(self):
        self.chat_widget.w_edit_message.reply_to(self.message)
        self.chat_widget.set_focus('MESSAGE_EDIT')

    @keymaps.MESSAGE_LIST_ITEM.command
    def mention_author(self):
        self.chat_widget.w_edit_message.edit.insert_text("<@!{0}>".format(
            self.message.author.id))
        self.chat_widget.set_focus('MESSAGE_EDIT')

    @keymaps.MESSAGE_LIST_ITEM.command
    def yank_message(self):
        discurses.config.to_clipboard(self.message.clean_content)
        return

    @keymaps.MESSAGE_LIST_ITEM.command
    def select_channel(self):
        self.chat_widget.set_send_channel(self.message.channel)
        self.chat_widget.w_message_list.focus_message_textbox()

    class Column:
        def __init__(self,
                     name,
                     visible,
                     width,
                     content,
                     attr_map="body",
                     padding=(0, 0),
                     align="left"):
            self.name = name
            self.visible = visible
            self.width = width
            self.content = content
            self.attr_map = attr_map
            self.padding = padding
            self.align = align

        def get_widget(self):
            txt = urwid.Text(self.content, align=self.align)
            if self.padding[0] > 0 or self.padding[1] > 0:
                txt = urwid.Padding(
                    txt, left=self.padding[0], right=self.padding[1])
            return urwid.AttrMap(txt, self.attr_map)


class TopReachedWidget(urwid.WidgetWrap):
    """This widget will be displayed at the top of the channel history"""

    def __init__(self, chat_widget):
        self.chat_widget = chat_widget
        self.message = FakeMessage(datetime.datetime.min)
        self._selectable = False
        txt = urwid.Text(
            "                                                               \n"
            "                                                               \n"
            "                                                               \n"
            "                                                               \n"
            "< moo >                                                        \n"
            " -----                                                         \n"
            "        \   ^__^                                               \n"
            "         \  (oo)\_______                                       \n"
            "            (__)\       )\/\                                   \n"
            "                ||----w |                                      \n"
            "                ||     ||                                      \n"
            "                                                               \n"
            "                                                               \n"
            "Congratulations! You have reached the top, Thats awesome! Unless "
            "the channel is empty, in which case, meh... big deal.\n\n",
            align=urwid.CENTER)
        w = urwid.Padding(txt, left=5, right=5)
        self.__super.__init__(w)

    def update_columns(*args, **kwargs):
        pass


class ForbiddenWidget(urwid.WidgetWrap):
    """This widget will be displayed in channels you can't access"""

    def __init__(self, chat_widget):
        self.chat_widget = chat_widget
        self.message = FakeMessage(datetime.datetime.min)
        self._selectable = False
        txt = urwid.Text(
            "                                                               \n"
            "                                                               \n"
            "                                                               \n"
            "                                                               \n"
            "< moo >                                                        \n"
            " -----                                                         \n"
            "        \   ^__^                                               \n"
            "         \  (oo)\_______                                       \n"
            "            (__)\       )\/\                                   \n"
            "                ||----w |                                      \n"
            "                ||     ||                                      \n"
            "                                                               \n"
            "                                                               \n"
            "Oops! This channel is Forbidden. You don't have access. Sorry!\n",
            align=urwid.CENTER)
        w = urwid.Padding(txt, left=5, right=5)
        self.__super.__init__(w)

    def update_columns(*args, **kwargs):
        pass


class DatelineWidget(urwid.WidgetWrap):
    """Displays a date separator in the listwidget"""

    def __init__(self, chat_widget, date):
        self.chat_widget = chat_widget
        self.message = FakeMessage(
            datetime.datetime.combine(date,
                                      datetime.datetime.min.time()))
        self._selectable = False
        txt = urwid.Text(("dateline", date.strftime("%d.%m.%Y")),
                         align=urwid.LEFT)
        self.__super.__init__(txt)

    def update_columns(*args, **kwargs):
        pass


class FakeMessage:
    """Very much a temporary thing"""

    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.id = "0"


