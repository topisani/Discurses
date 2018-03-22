import os

import urwid
import discord

import discurses.keymaps as keymaps


class MemberList(urwid.WidgetWrap):
    def __init__(self, chat_widget):
        self.chat_widget = chat_widget
        self.list_walker = urwid.SimpleListWalker([])
        self.w_listbox = urwid.ListBox(self.list_walker)
        self.update_list()
        self.__super.__init__(urwid.Padding(self.w_listbox, left=2))
        keymaps.GLOBAL.add_command("redraw", self.update_list)

        def updlst(*args, **kwargs):
            self.update_list()
        self.chat_widget.discord.add_event_handler("on_member_join", updlst)
        self.chat_widget.discord.add_event_handler("on_member_remove", updlst)
        self.chat_widget.discord.add_event_handler("on_member_update", updlst)

    def _get_user_attr(self, member):
        if member.status == discord.Status.online:
            return "sidebar_user_on"
        if member.status == discord.Status.offline:
            return "sidebar_user_off"
        if member.status == discord.Status.idle:
            return "sidebar_user_idle"

    def mouse_event(self, size, event, button, col, row, focus):
        if event == 'mouse press':
            if button == 4:
                return self.w_listbox.keypress(size, "up") is not None
            if button == 5:
                return self.w_listbox.keypress(size, "down") is not None
        return self.w_listbox.mouse_event(size, event, button, col, row, focus)

    def update_list(self):
        async def callback():
            servers = set()
            memberset = set()
            for ch in self.chat_widget.channels:
                if not ch.is_private:
                    servers.add(ch.server)
            for serv in servers:
                for member in serv.members:
                    memberset.add(member)
            items = []
            on = []
            idle = []
            off = []
            for member in memberset:
                if member.status == discord.Status.online:
                    on.append(member)
                if member.status == discord.Status.offline:
                    off.append(member)
                if member.status == discord.Status.idle:
                    idle.append(member)
            members = on + idle + off
            for member in members:
                items.append(
                    urwid.AttrMap(
                        urwid.Padding(
                            urwid.Text(member.display_name), left=1, right=1),
                        self._get_user_attr(member),
                        self._get_user_attr(member)))
            self.list_walker[:] = items

        self.chat_widget.discord.async(callback())
