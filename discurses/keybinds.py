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
        self.keys = keys

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
        If the key is already mapped, the command will be added to its list
        """
        if key in self.keys.keys():
            self.keys[key].append(command)
        else:
            self.keys[key] = [command]

    def command(self, func):
        """
        Decorator, used to bind `func` to `command`
        """
        self.add_command(func.__name__, func)
        return func
 
    def keypress(self, func):
        """
        Decorator
        Calls the apropriate commands for the keypress,
        and then calls the decorated function
        """
        def dec(widget, size, key):
            k = None
            if key in self.keys.keys():
                for command in self.keys[key]:
                    assert command in self.commands
                    for fn in self.commands[command]:
                        nk = fn(widget, size, key)
                        k = nk if nk is not None else k
            func(widget, size, k)
        return dec

    def owner(self, clazz):
        """
        Class Decorator.
        Adds a `keypress` method to the class.
        Do not use, this if the class needs to implement its own `keypress` method.
        Instead, decorate the keypress with `keypress`
        """
        @self.keypress
        def _keypress(w, size, key):
            return key
        clazz.keypress = _keypress
        return clazz
