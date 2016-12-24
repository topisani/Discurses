import urwid

from discurses.ui.lib import TextEditWidget

class HasModal:

    def __init__(self, main_widget):
        self.main_widget = main_widget
        self.pop_up = urwid.Frame(urwid.WidgetPlaceholder(None))
        self.w_placeholder = urwid.WidgetPlaceholder(self.main_widget)
        self.pop_up_overlay = urwid.Overlay(
            urwid.LineBox(self.pop_up), self.main_widget, 'center', ('relative', 60),
            'middle', ('relative', 60))

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
        self.pop_up.set_focus("body")


    def open_text_prompt(self, callback, title="", content=""):
        self.open_pop_up(
            urwid.Filler(TextEditWidget(
                callback, content=content)),
            header=urwid.Text(
                title, align='center'),
            height=6,
            width=50)

    def open_confirm_prompt(self, callback, title="", content="", yestxt="Yes", notxt="No"):
        def create_cb(bool):
            def res(*k, **a):
                callback(bool)
                self.close_pop_up()
            return res
        self.open_pop_up(
            urwid.Filler(urwid.Text(content, align='center')),
            header=urwid.Text(
                title, align='center'),
            footer=urwid.Columns([
                (urwid.Button(yestxt, create_cb(True))),
                (urwid.Button(notxt, create_cb(False))),
            ]),
            height=6,
            width=50)
        self.pop_up.set_focus("footer")

    def close_pop_up(self):
        self.pop_up.body.original_widget = None
        self.pop_up.header = None
        self.pop_up.footer = None
        self.pop_up_overlay.set_overlay_parameters('center', ('relative', 60),
                                                   'middle', ('relative', 60))
        self.w_placeholder.original_widget = self.main_widget
