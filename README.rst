Discurses
=========

|PyPI version|

A CLI for discord, written in Python. The name is a combination of
discord and curses, as in the terminal interface library. Discurses
doesn’t use curses, but i originally planned to. It is now built using
urwid, a widget library which *can* use curses as a rendering engine,
but discurses works fine without it.

Questions, bug reports, PR’s and comments are all very welcome.

I can be contacted at ``topisani@hamsterpoison.com`` |Discurses chat
view|

Installation
------------

Linux
~~~~~

That one is pretty easy:

.. code:: shell

    $ pip install discurses

Python 3.6 or more is required.

If you're having trouble launching the application post-install, check
your PATH variable.

.. code:: shell

    $ echo $PATH

Pip installs by default into $HOME/.local/bin which is not typically
part of your path. You can add it with the following command:

.. code:: shell

    $ export PATH=$PATH:$HOME/.local/bin

Note: this is a temporary fix, you would need to add $HOME/.local/bin to
your .profile or .bashrc to make it permanent, check your distributions
documentation for PATH settings.

Windows
~~~~~~~

Start out by following
`this <https://wiki.archlinux.org/index.php/Installation_guide>`__
guide.

After that, follow the instructions for linux above

Seriously: urwid is *sadly* not supported on Windows, and since
discurses is built on top of that, such an OS is not supported. You may
use the official desktop client anyway.

Authentication
--------------

Put the file ``example_discurses.yaml`` in your ``~/.config/``
directory, replace the placeholder with your discord token and rename
the file to ``discurses.yaml``. You can get the token by visiting
[https://discordapp.com/channels/@me](https://discordapp.com/channels/@me),
opening the developer tools (Ctrl+shift+i or Command+shift+i) and Click
on the ``Application`` tab, then on the sidebar: ``Local Storage`` then
click the URL from the dropdown and you should see the ``token`` key
followed by your token, copy whats inside the speech marks and put it in
your ``.yaml`` file.

Usage
-----

Full list available in discurses/keymaps.py…

When your cursor is in the text box:

+--------------+---------------------------+
| Key          | Action                    |
+==============+===========================+
| enter        | send message              |
+--------------+---------------------------+
| meta + enter | insert newline            |
+--------------+---------------------------+
| down         | show channel seclector    |
+--------------+---------------------------+
| up           | focus on the message list |
+--------------+---------------------------+
| esc          | cancel message            |
+--------------+---------------------------+

General Commands:

+----------+--------------------+
| Key      | Action             |
+==========+====================+
| meta + s | toggle server list |
+----------+--------------------+
| meta + b | toggle member list |
+----------+--------------------+
| meta + q | quit               |
+----------+--------------------+

Contributing
------------

First of all, please do, and if you do, feel free to ask me any
questions. Also, the issue reports are up for grabs, but id be very
happy to be notified before you start work, just so we dont work on the
same thing.

.. |PyPI version| image:: https://badge.fury.io/py/discurses.svg
   :target: https://badge.fury.io/py/discurses
.. |Discurses chat view| image:: https://github.com/topisani/Discurses/raw/master/docs/graphics/img-2016-10-06-142806.png

