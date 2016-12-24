import logging

logger = logging.getLogger(__name__)

def parameterized(dec):
    """
    Meta decorator.
    Decorate a decorator that accepts the decorated function as first argument,
    and then other arguments with this decorator, to be able to pass it arguments.

    Source: http://stackoverflow.com/a/26151604
    
    >>> @parameterized
    ... def multiply(f, n):
    ...     def dec(*args, **kwargs):
    ...         return f(*args, **kwargs) * n
    ...     return dec
    >>> @multiply(5)
    ... def add(a, b):
    ...     return a + b
    >>> add(3, 2)
    25
    """

    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl

    return layer


class KeyMap:
    """
    A keymap contains two things:
    A list of commands, defined using the `@keybind` decorator,
    and a list of key to command mappings.
    """

    def __init__(self, keys={}):
        self.commands = {}
        self.keys = {}
        for key, commands in keys.items():
            self.add_key(key, commands)

    def add_command(self, name, func):
        """
        Add a command to the command map.
        If the command already exists, the function will be added to the list
        """
        if name in self.commands.keys():
            self.commands[name].append(func)
        else:
            self.commands[name] = [func]

    def add_key(self, key, command):
        """
        Map `key` to `command`
        command can be one of the following:

          * A string, the name of the command
          * A tuple `(command, args...)`. `args` will be passed to the
            functions
          * A list of any of the two above, can be mixed

        If the key is already mapped, the command will be added to its list
        """
        if not isinstance(command, list) and not isinstance(command, set):
            command = {command}
        for c in command:
            if not isinstance(c, tuple):
                c = (c,)
            if key in self.keys.keys():
                self.keys[key].append(c)
            else:
                self.keys[key] = [c]

    def command(self, func):
        """
        Decorator, used to bind `func` to `command`
        """
        self.add_command(func.__name__, func)
        return func

    def keypress(self, func):
        """
        Decorator
        Calls the decorated function before calling the apropriate commands
        for the keypress. The value returned by `func` will be sent to the
        commands as the new `key`
        """

        def dec(widget, size, key):
            key = func(widget, size, key)
            return self.press_key(key, widget)

        return dec

    def press_key(self, key, widget):
        """
        Calls the commands associated with `key`
        Will return `None` or the result of the last command that wasnt `None`
        """
        k = key
        if key in self.keys.keys():
            k = None
            for command in self.keys[key]:
                assert command[0] in self.commands
                if len(command) > 1:
                    nk = self.call_command(command[0], widget, *command[1:])
                else:
                    nk = self.call_command(command[0], widget)
                if nk is not None:
                    k = nk
        return k

    def call_command(self, command, *args, **kwargs):
        """
        Call command by name and pass it `*args` and `**kwargs`
        Will return `None` or the result of the last function that wasnt `None`
        """
        key = None
        logger.debug("Calling %d commands for '%s'", len(self.commands[command]), command)
        for fn in self.commands[command]:
            k = fn(*args, **kwargs)
            if k is not None:
                key = k
        return key
