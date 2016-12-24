import discord
import urwid

import discurses.keymaps as keymaps


class ServerTree(urwid.WidgetWrap):
    def __init__(self, chat_widget, close_callback=None):
        self.chat_widget = chat_widget
        self.ui = chat_widget.ui
        self.close_callback = close_callback
        items = []
        for server in sorted(chat_widget.discord.servers, key=lambda s: s.name):
            node = {"name": server.name,
                    'server_tree': self,
                    'server': server,
                    "children": []}
            for ch in server.channels:
                if ch.type == discord.ChannelType.text:
                    node['children'].append({
                        'name': ch.name,
                        'server_tree': self,
                        'channel': ch
                    })

            nodeobj = TreeNodeServer(node)
            nodeobj.expanded = False
            items.append(nodeobj)

        self.w_listbox = urwid.TreeListBox(TreeWalker(items))
        self.__super.__init__(self.w_listbox)

    def selectable(self):
        return True

    @keymaps.SERVER_TREE.keypress
    def keypress(self, size, key):
        return self.w_listbox.keypress(size, key)

    @keymaps.SERVER_TREE.command
    def close(self):
        if self.close_callback:
            self.close_callback()

class TreeWidgetChannel(urwid.TreeWidget):
    def get_display_text(self):
        return self.get_node().get_value()['name']

    def load_inner_widget(self):
        return urwid.AttrMap(
            urwid.Text(self.get_display_text()), "servtree_channel",
            "servtree_channel_f")

    @keymaps.SERVER_TREE_CHANNEL.keypress
    def keypress(self, size, key):
        return key

    @keymaps.SERVER_TREE_CHANNEL.command
    def select(self):
        server_tree = self.get_node().get_value()['server_tree']
        channel = self.get_node().get_value()['channel']
        server_tree.chat_widget.channels.append(channel)
        server_tree.chat_widget.send_channel = channel
        server_tree.chat_widget.channel_list_updated()

    @keymaps.SERVER_TREE_CHANNEL.command
    def set_only(self, set_name=True):
        server_tree = self.get_node().get_value()['server_tree']
        channel = self.get_node().get_value()['channel']
        server_tree.chat_widget.channels[:] = [channel]
        server_tree.chat_widget.send_channel = channel
        server_tree.chat_widget.channel_list_updated()
        if set_name:
            server_tree.chat_widget.set_name("{}#{}".format(
                channel.server.name, channel.name))

    @keymaps.SERVER_TREE_CHANNEL.command
    def exit(self):
        server_tree = self.get_node().get_value()['server_tree']
        server_tree.close()

    def selectable(self):
        return True


class TreeWidgetServer(urwid.TreeWidget):
    def __init__(self, node):
        self._node = node
        self._innerwidget = None
        self.is_leaf = False
        self.expanded = False
        widget = self.get_indented_widget()
        urwid.WidgetWrap.__init__(self, widget)

    def get_display_text(self):
        return self.get_node().get_value()['name'] + ": " + str(
            len(self.get_node().get_value()['children']))

    def load_inner_widget(self):
        return urwid.AttrMap(
            urwid.Text(self.get_display_text()), "servtree_server",
            "servtree_server_f")

    @keymaps.SERVER_TREE_SERVER.keypress
    def keypress(self, size, key):
        return urwid.TreeWidget.keypress(self, size, key)

    @keymaps.SERVER_TREE_SERVER.command
    def expand(self):
        urwid.TreeWidget.keypress(self, (0, 0), "+")

    @keymaps.SERVER_TREE_SERVER.command
    def collapse(self):
        urwid.TreeWidget.keypress(self, (0, 0), "-")

    @keymaps.SERVER_TREE_SERVER.command
    def toggle(self):
        if self.expanded:
            self.collapse()
        else:
            self.expand()

    @keymaps.SERVER_TREE_SERVER.command
    def set_only(self, set_name=True):
        server_tree = self.get_node().get_value()['server_tree']
        children = self.get_node().get_value()['children']
        server_tree.chat_widget.channels = sorted(
                                                [ ch.get('channel') for ch in children ],
                                            key=lambda c: c.name)
        server_tree.chat_widget.send_channel = next((c for c in server_tree.chat_widget.channels
                                                     if c.name == "general"
                                                    ), server_tree.chat_widget.channels[0])
        server_tree.chat_widget.channel_list_updated()
        if set_name:
            server_tree.chat_widget.set_name(self.get_node().get_value()[
                'server'].name)

    @keymaps.SERVER_TREE_SERVER.command
    def exit(self):
        server_tree = self.get_node().get_value()['server_tree']
        server_tree.close()


class TreeNodeChannel(urwid.TreeNode):
    def load_widget(self):
        return TreeWidgetChannel(self)


class TreeNodeServer(urwid.ParentNode):
    def load_widget(self):
        return TreeWidgetServer(self)

    def load_child_keys(self):
        data = self.get_value()
        return range(len(data['children']))

    def load_child_node(self, key):
        childdata = self.get_value()['children'][key]
        childdepth = self.get_depth() + 1
        return TreeNodeChannel(
            childdata, parent=self, key=key, depth=childdepth)


class TreeWalker(urwid.ListWalker):
    """ListWalker-compatible class for displaying TreeWidgets

    positions are TreeNodes."""

    def __init__(self, trees):
        """start_from: TreeNode with the initial focus."""
        self.focus = trees[0]
        self.trees = trees
        self.focus_tree = 0

    def get_focus(self):
        widget = self.focus.get_widget()
        return widget, self.focus

    def set_focus(self, focus):
        self.focus = focus
        self._modified()

    def get_next(self, start_from):
        widget = start_from.get_widget()
        target = widget.next_inorder()
        serv = start_from.get_parent() if type(
            start_from) == TreeNodeChannel else start_from
        index = self.trees.index(serv)
        if target is None and index < len(self.trees) - 1:
            target = self.trees[index + 1].get_widget()
        if target is None:
            return None, None
        else:
            return target, target.get_node()

    def get_prev(self, start_from):
        widget = start_from.get_widget()
        target = widget.prev_inorder()
        serv = start_from.get_parent() if type(
            start_from) == TreeNodeChannel else start_from
        index = self.trees.index(serv)
        if target is None and index > 0:
            target = self.trees[index - 1].get_widget()
        if target is None:
            return None, None
        else:
            return target, target.get_node()
