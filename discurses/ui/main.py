import re

import urwid

from discurses.ui import HasModal
from discurses.ui import ChatWidget
from discurses import keymaps


class MainUI(HasModal):
    palette = [
        ("focus", "dark red", "", "standout"),
        ("dim", "dark cyan", "", "standout"),
        ("head", "light red", ""),
        ("message_timestamp", "dark cyan", "", ""),


        ("message_channel", "light green", "", "bold"),
        ("message_author", "light blue", "", ""),
        ("message_content", "white", "", ""),
        ("message_channel_cur", "dark green", "", ""),
        ("message_timestamp_f", "black", "dark cyan", "bold"),
        ("message_channel_f", "black", "light green", "bold"),
        ("message_author_f", "black", "light blue", "bold"),
        ("message_content_f", "black", "white", ""),
        ("message_channel_cur_f", "black", "dark green", "bold"),
        ("message_mention", "white", "dark gray", "standout"),
        ("message_mention_f", "white", "dark gray", "standout"),
        ("message_mention_self", "light green", "dark gray", ""),
        ("message_mention_self_f", "light green", "dark gray", ""),
        ("send_channel_selector", "light red", "", ""),
        ("send_channel_selector_f", "black", "light red", ""),
        ("send_channel_selector_sel", "", "dark red", ""),
        ("send_channel_selector_sel_f", "black", "light red", ""),
        ("servtree_channel", "", "", ""),
        ("servtree_channel_f", "black", "white", "bold"),
        ("servtree_server", "", "", ""),
        ("servtree_server_f", "black", "white", "bold"),
        ("sidebar_user_on", "dark green", "", ""),
        ("sidebar_user_off", "dark red", "", ""),
        ("sidebar_user_idle", "yellow", "", ""),
        ("sidebar_user_on_f", "black", "dark green", ""),
        ("sidebar_user_off_f", "black", "dark red", ""),
        ("sidebar_user_idle_f", "black", "yellow", ""),
        ("tab_selector_tab", "black", "light gray", ""),
        ("tab_selector_tab_f", "light gray", "", ""),
    ]

    def __init__(self, discord_client):
        self.discord = discord_client
        self.tabs = {}
        self.w_tabs = TabSelector(self)
        self.frame = urwid.Frame(
            urwid.Filler(
                urwid.Text(
                    """
░█▀▄░▀█▀░█▀▀░█▀▀░█░█░█▀▄░█▀▀░█▀▀░█▀▀
░█░█░░█░░▀▀█░█░░░█░█░█▀▄░▀▀█░█▀▀░▀▀█
░▀▀░░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀
                              v0.2.1


 < Logging in... Hang tight! >
  --------------------------- 
         \   ^__^             
          \  (oo)\_______     
             (__)\       )\/\ 
                 ||----w |    
                 ||     ||    



        """,
                    align=urwid.CENTER)),
            header=self.w_tabs)

        HasModal.__init__(self, self.frame)

        self.urwid_loop = urwid.MainLoop(
            self.w_placeholder,
            palette=MainUI.palette,
            unhandled_input=lambda key: self._keypress(None, key),
            event_loop=urwid.AsyncioEventLoop(loop=self.discord.loop),
            pop_ups=True)

        def refresh(_loop, _data):
            _loop.draw_screen()
            _loop.set_alarm_in(2, refresh)

        self.urwid_loop.set_alarm_in(0.2, refresh)

        self.urwid_loop.start()


    @keymaps.GLOBAL.keypress
    def _keypress(self, nothing, input):
        if input is None or type(input) != str:
            return
        match = re.fullmatch("meta ([0-9])", input)
        if match is not None:
            index = int(match.group(1))
            self.notify("Tab: {0}".format(index))
            if index == 0:
                index = 10
            self.set_tab(index - 1)

    @keymaps.GLOBAL.command
    def quit(widget, size, key):
        widget.urwid_loop.stop()
        raise urwid.ExitMainLoop()

    @keymaps.GLOBAL.command
    def focus_tab_selector(widget, size, key):
        widget.frame.set_focus('header')

    @keymaps.GLOBAL.command
    def redraw(widget, size, key):
        widget.draw_screen()
    
    def set_tab(self, tab):
        if tab not in self.tabs.keys():
            self.tabs[tab] = (ChatWidget(
                self.discord, [], None, name=str(tab + 1)))
        self.w_tabs.update_columns(tab)
        self.set_body(self.tabs[tab])

    def set_body(self, w):
        self.frame.set_body(w)
        self.draw_screen()

    def notify(self, string):
        pass

    def draw_screen(self):
        self.urwid_loop.draw_screen()

    def on_ready(self):
        self.set_tab(0)


class TabSelector(urwid.WidgetWrap):
    def __init__(self, ui):
        self.ui = ui
        self.w_cols = urwid.Columns([])
        self._selectable = True
        self.update_columns()
        self.__super.__init__(self.w_cols)

    def selectable(self):
        return True

    @keymaps.TAB_SELECTOR.keypress
    def keypress(self, size, key):
        return key

    @keymaps.TAB_SELECTOR.command
    def go_left(self, size, key):
        self.w_cols.focus_position = (
            self.w_cols.focus_position - 1) % len(self.w_cols.widget_list)
        self.ui.set_tab(self.w_cols.focus.index)

    @keymaps.TAB_SELECTOR.command
    def go_right(self, size, key):
        self.w_cols.focus_position = (
            self.w_cols.focus_position + 1) % len(self.w_cols.widget_list)
        self.ui.set_tab(self.w_cols.focus.index)

    @keymaps.TAB_SELECTOR.command
    def unfocus(self, size, key):
        self.ui.frame.set_focus("body")

    @keymaps.TAB_SELECTOR.command
    def delete_tab(self, size, key):
        del self.ui.tabs[self.w_cols.focus.index]
        self.update_columns()

    @keymaps.TAB_SELECTOR.command
    def new_tab(self, size, key):
        self.ui.set_tab(len(self.ui.tabs))

    def _set_indicator(self, position):
        for col in self.w_cols.contents:
            col[0].attr.set_attr_map({None: "tab_selector_tab"})
        self.w_cols.contents[position][0].attr.set_attr_map({None: "tab_selector_tab_f"})
        
    def update_columns(self, focus=None):
        cols = []
        for index, tab in self.ui.tabs.items():
            cols.append((self.TabWidget(index, tab),
                            self.w_cols.options('weight', 1)))
        self.w_cols.contents = cols
        for t, options in self.w_cols.contents:
            if t.index == focus:
                self.w_cols.focus_position = self.w_cols.contents.index((t, options))
                break
        if not cols == []:
            self._set_indicator(self.w_cols.focus_position)

    class TabWidget(urwid.WidgetWrap):

        def __init__(self, index, widget):
            self.index = index
            self.tab_widget = widget
            self.attr = urwid.AttrMap(
                urwid.Text(
                    widget.name, align="center"),
                "tab_selector_tab")
            self.__super.__init__(self.attr)


