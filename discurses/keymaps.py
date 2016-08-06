from discurses.keybinds import KeyMap

GLOBAL = KeyMap({
    "ctrl q": ["quit"],
    "ctrl l": ["redraw"],
    "ctrl t": ["focus_tab_selector"],
    "meta t": ["focus_tab_selector"],
})

TAB_SELECTOR = KeyMap({
    "left": ["go_left"],
    "right": ["go_right"],
    "enter": ["unfocus"],
    "esc": ["unfocus"],
    "d": ["delete_tab"],
    "delete": ["delete_tab"],
    "n": ["new_tab"],
})
