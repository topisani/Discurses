"""
Everything UI
"""
import asyncio
import datetime
import sys
from typing import List

import urwid
import discord
from discord import Channel, Message

import config
from main import DiscordClient

class MainUI:
    palette = [
        ("message", "white", "", "standout"),
        ("time", "dark cyan", "", "standout"),
        ("author", "dark green", "", "standout"),
        ("focus", "dark red", "", "standout"),
        ("dim", "dark cyan", "", "standout"),
        ("head", "light red", ""),
    ]

    def __init__(self, discord_client: DiscordClient):
        self.discord = discord_client
        header = urwid.AttrMap(urwid.Text("Logging in"), "head")
        self.frame = urwid.Frame(
            urwid.Filler(urwid.Text("""
 ___________________________ 
< Logging in... Hang tight! >
 --------------------------- 
        \   ^__^             
         \  (oo)\_______     
            (__)\       )\/\ 
                ||----w |    
                ||     ||    

        """, align=urwid.CENTER)), header=header)
        self.urwid_loop = urwid.MainLoop(
            self.frame,
            palette=MainUI.palette,
            unhandled_input=self._keypress,
            event_loop=urwid.AsyncioEventLoop(loop=self.discord.loop),
            pop_ups=True)

        def refresh(_loop, _data):
            _loop.draw_screen()
            _loop.set_alarm_in(2, refresh)

        self.urwid_loop.set_alarm_in(0.2, refresh)

        self.urwid_loop.start()

    def _keypress(self, input):
        if input in ("q", "Q"):
            self.urwid_loop.stop()

    def set_body(self, w):
        self.frame.set_body(w)
        self.draw_screen()

    def notify(self, string):
        string = str(string)
        self.frame.set_header(urwid.AttrWrap(urwid.Text(string), "head"))

    def draw_screen(self):
        self.urwid_loop.draw_screen()

    def on_ready(self):
        channel = self.discord.get_channel(str(sys.argv[1]))
        assert channel is not None
        self.set_body(ChatWidget(self.discord, [channel], channel))


class ChatWidget(urwid.WidgetWrap):
    """This widget holds:
        1. A MessageListWidget of all the messages in channels
        2. A EditMessageWidget, sending messages to send_channel
    """

    def __init__(self, discord_client: DiscordClient, channels: List[Channel],
                 send_channel: Channel):
        self.discord = discord_client
        self.ui = self.discord.ui
        self.channels = channels
        self.send_channel = send_channel
        self._selectable = False

        self.message_list = MessageListWidget(self.discord, self, channels)
        self.edit_message = MessageEditWidget(self.discord, self, send_channel)
        self.frame = urwid.Pile([('weight', 1, self.message_list), ('pack', self.edit_message)], 1)
        self.__super.__init__(self.frame)


class MessageListWidget(urwid.WidgetWrap):
    """The Listbox of MessageWidgets"""

    def __init__(self, discord_client: DiscordClient, chat_widget: ChatWidget,
                 channels: List[Channel]):
        self.discord = discord_client
        self.ui = self.discord.ui
        self.chat_widget = chat_widget
        self.channels = channels
        self.list_walker = MessageListWalker(self)
        self.listbox = urwid.ListBox(self.list_walker)
        self.discord.add_event_handler('on_message', self._on_message)
        self.discord.add_event_handler('on_message_edit',
                                       self._on_message_edit)
        self.discord.add_event_handler('on_message_delete',
                                       self._on_message_delete)
        self.scroll_to_bottom()
        self.__super.__init__(self.listbox)

    def add_message(self, message: Message):
        self.list_walker.append(
            MessageWidget(self.discord, self.chat_widget, message))
        focus_status, focus = self.list_walker.get_focus()
        if not focus > len(self.list_walker) - 2:
            self.scroll_to_bottom()
        self.discord.ui.draw_screen()

    def _on_message(self, message: Message):
        if message.channel in self.channels:
            self.add_message(message)

    def _on_message_edit(self, before: Message, after: Message):
        if before.channel in self.channels:
            for mw in self.list_walker:
                if before.id == mw.message.id:
                    index = self.list_walker.index(mw)
                    self.list_walker[index] = MessageWidget(
                        self.discord, self.chat_widget, after)
                    break

    def _on_message_delete(self, m: Message):
        if m.channel in self.channels:
            for mw in self.list_walker:
                if m.id == mw.message.id:
                    self.list_walker.remove(mw)
                    break

    def scroll_to_bottom(self):
        if len(self.list_walker) > 0:
            self.listbox.set_focus(len(self.list_walker) - 1)

    def keypress(self, size, key):
        key = self._w.keypress(size, key)
        if key is None:
            return
        if key == "down":
            self.chat_widget._w.set_focus(self.chat_widget.edit_message)


class MessageListWalker(urwid.MonitoredFocusList, urwid.ListWalker):
    def __init__(self, list_widget: MessageListWidget):
        self.list_widget = list_widget
        self.is_polling = False
        self.top_reached = False
        urwid.MonitoredFocusList.__init__(self, [])
        self.get_logs(callback=list_widget.scroll_to_bottom)

    def get_logs(self, before=None, callback=lambda: None):
        if before == None and len(self) > 0:
            before = self[0].message.timestamp
        if self.is_polling or self.top_reached:
            return
        self.is_polling = True

        async def _callback():
            messages = []
            for channel in self.list_widget.channels:
                async for m in self.list_widget.discord.logs_from(
                    channel, before=before):
                    messages.append(
                        MessageWidget(self.list_widget.discord,
                                      self.list_widget.chat_widget, m))
            if messages == []:
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
        for mw in self:
            if mw.message.id in st:
                self.remove(mw)
            else:
                st.append(mw.message.id)
        self.sort(key=lambda mw: mw.message.timestamp)

    def _modified(self):
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

    def __init__(self, discord_client: DiscordClient, chat_widget: ChatWidget,
                 m: Message):
        self.discord = discord_client
        self.ui = self.discord.ui
        self.chat_widget = chat_widget
        self.message = m
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

    def selectable(self) -> bool:
        return True

    def keypress(self, size, key: str):
        if key == "enter" and self.message.author == self.discord.user:
            self.chat_widget.edit_message.edit_message(self.message)
            self.chat_widget.frame.set_focus(self.chat_widget.edit_message)
        if key == "delete" and (self.message.author == self.discord.user or
                                self.message.channel.permissions_for(
                                    self.discord.user).manage_messages):
            self.discord.async(self.discord.delete_message(self.message))
        if key == "r":
            self.chat_widget.edit_message.reply_to(self.message)
            self.chat_widget.frame.set_focus(self.chat_widget.edit_message)
        return key


class MessageEditWidget(urwid.WidgetWrap):
    """Wrapper for Edit widget, mainly to allow capturing keypresses"""

    def __init__(self, discord_client: DiscordClient, chat_widget: ChatWidget,
                 channel):
        self.discord = discord_client
        self.ui = self.discord.ui
        self.chat_widget = chat_widget
        self.channel = channel
        self.editing = None
        self.caption = urwid.Text("\n Send ")
        self.edit = urwid.Edit(multiline=True)
        lb = urwid.LineBox(urwid.Padding(self.edit, left=1, right=1))
        w = urwid.Columns([('pack', self.caption), ('weight', 1, lb)])
        self.__super.__init__(w)

    def selectable(self) -> bool:
        # This is where we can disable the edit widget
        # if the user is missing permissions
        return True

    def _send_message(self):
        if self.edit.edit_text == "":
            self.stop_edit()
            return
        if self.editing is not None:
            self.discord.async(
                self.discord.edit_message(self.editing,
                                          self.edit.edit_text))
            self.stop_edit()
        else:
            self.discord.async(
                self.discord.send_message(self.channel,
                                          self.edit.edit_text))

    def keypress(self, size, key):
        if key == "enter":
            self._send_message()
            self.edit.set_edit_text("")
        elif key == "meta enter":
            self.edit.keypress(size, "enter")
        else:
            key = self.edit.keypress(size, key)
            if key is None:
                return
            if key == "up":
                self.chat_widget.frame.set_focus(self.chat_widget.message_list)
                self.chat_widget.message_list.scroll_to_bottom()
            if key == "escape":
                if self.editing is not None:
                    self.stop_edit()
                else:
                    self.chat_widget.frame.edit_message.set_focus(self.chat_widget.message_list)

    def edit_message(self, message: Message):
        self.caption.set_text("\n Edit ")
        self.editing = message
        self.edit.set_edit_text(message.content)
        self.edit.set_edit_pos(len(self.edit.edit_text))

    def reply_to(self, message: Message):
        self.edit.set_edit_text("> _{0}_\n".format(message.content))
        self.edit.set_edit_pos(len(self.edit.edit_text))

    def stop_edit(self):
        self.caption.set_text("\n Send ")
        self.editing = None
        self.edit.set_edit_text("")


class TopReachedWidget(urwid.WidgetWrap):
    """This widget will be displayed at the top of the channel history"""

    def __init__(self, chat_widget: ChatWidget):
        self.chat_widget = chat_widget
        self.message = FakeMessage()
        self._selectable = False
        txt = urwid.Text("""

        
 _____                        
< moo >                       
 -----                        
        \   ^__^              
         \  (oo)\_______      
            (__)\       )\/\  
                ||----w |     
                ||     ||     

        
Congratiulations! You have reached the top, Thats awesome! Unless the channel is empty, in which case, meh... big deal.\n\n""",
            align=urwid.CENTER)
        w = urwid.Padding(txt, left=5, right=5)
        self.__super.__init__(w)

class FakeMessage:
    """Very much a temporary thing"""

    def __init__(self):
        self.timestamp = datetime.datetime.min
        self.id = "0"
