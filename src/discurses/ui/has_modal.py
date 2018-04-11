import urwid

from discurses.ui.lib import TextEditWidget
import logging

logger = logging.getLogger(__name__)


class HasModal:

    def __init__(self, main_widget):
        self._main_widget = main_widget
        self._pop_up = urwid.Frame(urwid.WidgetPlaceholder(None))
        self._w_placeholder = urwid.WidgetPlaceholder(self._main_widget)
        self._pop_up_overlay = urwid.Overlay(urwid.LineBox(self._pop_up),
                                            self._main_widget,
                                            'center',
                                            ('relative', 60),
                                            'middle',
                                            ('relative', 60))

    def open_pop_up(self,
                    widget,
                    header=None,
                    footer=None,
                    height=('relative', 60),
                    width=('relative', 60)):
        self._pop_up.body.original_widget = widget
        self._pop_up.header = header
        self._pop_up.footer = footer
        self._pop_up_overlay.set_overlay_parameters('center', width, 'middle',
                                                    height)
        self._w_placeholder.original_widget = self._pop_up_overlay
        self._pop_up.set_focus("body")

    def open_text_prompt(self, callback, title="", content=""):
        self.open_pop_up(
            urwid.Filler(TextEditWidget(
                callback, content=content)),
            header=urwid.Text(
                title, align='center'),
            height=6,
            width=50)

    def open_confirm_prompt(self, callback, title="", content="",
                            yestxt="Yes", notxt="No", align="center"):
        def create_cb(bool):
            def res(*k, **a):
                callback(bool)
                self.close_pop_up()
            return res
        self.open_pop_up(
            urwid.Filler(urwid.Text(content, align=align)),
            header=urwid.Text(
                title, align='center'),
            footer=urwid.Columns([
                (urwid.Button(yestxt, create_cb(True))),
                (urwid.Button(notxt, create_cb(False))),
            ]),
            height=6,
            width=50)
        self._pop_up.set_focus("footer")
        logger.debug("Confirm prompt text: " + str(content))

    def close_pop_up(self):
        self._pop_up.body.original_widget = None
        self._pop_up.header = None
        self._pop_up.footer = None
        self._pop_up_overlay.set_overlay_parameters('center', ('relative', 60),
                                                   'middle', ('relative', 60))
        self._w_placeholder.original_widget = self._main_widget
