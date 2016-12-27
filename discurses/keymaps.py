from discurses.keybinds import KeyMap

GLOBAL = KeyMap({
    "ctrl q": "quit",
    "ctrl l": "redraw",
    "ctrl t": "focus_tab_selector",
    "meta t": "focus_tab_selector",
})

TAB_SELECTOR = KeyMap({
    "left": "go_left",
    "right": "go_right",
    "enter": "unfocus",
    "esc": "unfocus",
    "d": "delete_tab",
    "delete": "delete_tab",
    "n": "new_tab",
})

CHAT = KeyMap({
    "meta s": "popup_server_tree",
    "up": "focus_up",
    "down": "focus_down",
    "meta n": "popup_rename_tab",
    "meta c": "popup_shell_command",
    "meta f": "popup_send_file",
    "ctrl l": "refetch_messages",
})

MESSAGE_LIST = KeyMap({
    "b": "toggle_sidebar",
    "esc": "focus_message_textbox"
})

MESSAGE_LIST_ITEM = KeyMap({
    "enter": "edit_message",
    "delete": "ask_delete_message",
    "r": ["quote_message", "select_channel"],
    "m": "mention_author",
    "y": "yank_message",
    "s": "select_channel",
})

MESSAGE_TEXT_BOX = KeyMap({
    "enter": "send_message",
    "meta enter": ("insert", "\n"),
    "down": "show_channel_selector",
    "up": "focus_message_list",
    "esc": "cancel_edit",
})

SEND_CHANNEL_SELECTOR = KeyMap({
    "left": "focus_left",
    "right": "focus_right",
    "enter": ["select_focused", "exit"],
    "esc": "exit",
    "up": "exit",
    "d": "delete_focused",
    "delete": "delete_focused",
})

SERVER_TREE = KeyMap({})

SERVER_TREE_CHANNEL = KeyMap({
    " ": "select",
    "enter": ["set_only", "exit"],
    "esc": "exit",
    "q": "exit"
})

SERVER_TREE_SERVER = KeyMap({
    " ": "toggle",
    "enter": ["set_only", "exit"],
    "esc": "exit",
    "q": "exit"
})

TEXT_EDIT_WIDGET = KeyMap({
    "enter": "save",
    "esc": "cancel",
})
