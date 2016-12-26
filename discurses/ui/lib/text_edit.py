import urwid
import discurses.keymaps as keymaps
import logging

logger = logging.getLogger(__name__)

class TextEditWidget(urwid.WidgetWrap):

    def __init__(self, callback, content=""):
        self.callback = callback
        self.w_edit = urwid.Edit(edit_text=content)
        self.w_lb = urwid.LineBox(self.w_edit)
        self.__super.__init__(self.w_lb)

    def selectable(self):
        return True

    @keymaps.TEXT_EDIT_WIDGET.keypress
    def keypress(self, size, key):
        return self.w_edit.keypress(size, key)

    @keymaps.TEXT_EDIT_WIDGET.command
    def save(self):
        self.callback(self.w_edit.edit_text)
        #self.w_edit.set_edit_text("")

    @keymaps.TEXT_EDIT_WIDGET.command
    def cancel(self):
        self.callback(None)


class EditWithOverlays(urwid.Edit):

    def __init__(self, caption=u"", edit_text=u"", multiline=False,
            align=urwid.LEFT, wrap=urwid.SPACE, allow_tab=False,
            edit_pos=None, layout=None, mask=None):
        self.overlays = ["Hi, my name is ", TextOverlay("<@!41378434659029>", "@SlimShady", "message_mention")]
        self.cur_overlay = len(self.overlays) - 1
        urwid.Edit.__init__(self, "")
        self.edit_text = self.get_text()[0]
        self.set_edit_pos(len(edit_text))

    def get_text(self):
        """
        Returns ``(text, display attributes)``. See :meth:`Text.get_text`
        for details.
        """

        attrib = []
        txt = ""
        for ol in self.overlays:
            if isinstance(ol, str):
                txt += ol
                attrib.append(("", len(ol)))
            elif isinstance(ol, TextOverlay):
                txt += ol.display_txt
                attrib.append((ol.attr, len(ol.display_txt)))
            else:
                logger.error("EditWithOverlays.get_text: Expected string or TextOverlay. Got ", ol.__class__)

        self.edit_text = txt
        return txt, attrib

    def keypress(self, size, key):
        p = self.edit_pos
        if key=="backspace":
            self.delete_char()
        else:
            return urwid.Edit.keypress(self, size, key)
        return None

    def insert_text(self, text):
        if len(self.overlays) == 0 or (not isinstance(self.overlays[self.cur_overlay], str)):
            self.overlays = self.overlays[:self.cur_overlay] + [text] + self.overlays[self.cur_overlay:]
        else:
            self.overlays[self.cur_overlay] = self.overlays[self.cur_overlay][:self.pos_in_ol] + text + self.overlays[self.cur_overlay][self.pos_in_ol:]
        self.set_edit_pos(self.edit_pos + len(text))
        self.get_text()

    def delete_char(self):
        if len(self.overlays) == 0:
            return None
        if isinstance(self.overlays[self.cur_overlay], str):
            if len(self.overlays[self.cur_overlay]) > 1:
                self.overlays[self.cur_overlay] = self.overlays[self.cur_overlay][:self.pos_in_ol -1] + self.overlays[self.cur_overlay][self.pos_in_ol:]
            else:
                self.overlays = self.overlays[:self.cur_overlay - 1] + self.overlays[self.cur_overlay:]
        else:
            self.overlays = self.overlays[:self.cur_overlay - 1] + self.overlays[self.cur_overlay:]
        self.edit_text = self.get_text()[0]
        self.edit_pos -= 1

    def set_edit_pos(self, pos):
        if pos < 0:
            pos = 0
        if pos > len(self._edit_text):
            pos = len(self._edit_text)
        if len(self.overlays) == 0:
            return None
        i = 0
        ol = self.overlays[i]
        l = 0
        while l + len(ol) < pos:
            i += 1
            if i < len(self.overlays):
                break
            ol = self.overlays[i]
            l += len(ol)
        self.cur_overlay = i
        self.pos_in_ol = pos - l
        self._edit_pos = pos
        self._invalidate()

class TextOverlay:
    def __init__(self, content, display_txt, attr):

        self.display_txt = display_txt
        self.content = content
        self.attr = attr

    def __len__(self):
        return len(self.display_txt)
