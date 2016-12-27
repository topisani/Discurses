import re
import logging

import urwid

from discurses.ui import HasModal
from discurses.ui import ChatWidget
from discurses import keymaps

logger = logging.getLogger(__name__)


def list_remove(lst, item):
    if item in lst:
        lst.remove(item)
    return lst

class MainUI(HasModal):
    palette = [
        ("focus",                     "dark red",        "default"  ),
        ("dim",                       "dark cyan",       "default"  ),
        ("head",                      "light red",       "default"  ),
        ("message_timestamp",         "dark cyan",       "default"  ),
        ("message_channel",           "light green",     "default"  ),
        ("message_author",            "light blue",      "default"  ),
        ("message_content",           "default",         "default"  ),
        ("message_channel_cur",       "dark green",      "default"  ),
        ("message_mention",           "white",           "dark gray"),
        ("message_mention_self",      "light green",     "dark gray"),
        ("send_channel_selector",     "light red",       "default"  ),
        ("send_channel_selector_sel", "default",         "dark red" ),
        ("servtree_channel",          "default",         "default"  ),
        ("servtree_server",           "default",         "default"  ),
        ("sidebar_user_on",           "dark green",      "default"  ),
        ("sidebar_user_off",          "dark red",        "default"  ),
        ("sidebar_user_idle",         "yellow",          "default"  ),
        ("tab_selector_tab",          "default,standout","default"  ),
        ("dateline",                  "dark red",        "default"  ),
    ]

    # A dict to replace colours on focus
    focus_attr = {c[0]: c[0] + "_f" for c in palette}

    # Add focus versions
    cols = [c[0] for c in palette]
    focus_palette = []
    for c in palette:
        if c[0] + "_f" not in cols:
            if "standout" not in c[1]:
                focus_palette.append((c[0] + "_f", c[1]+",standout", c[2]))
            else:
                logger.debug(c)
                focus_palette.append((c[0] + "_f", str.join(",", list_remove(c[1].split(","), "standout")), c[2]))

    palette += focus_palette

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
                              v0.2.2


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
        logger.debug("Keypres reached global map: %s", input)
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


