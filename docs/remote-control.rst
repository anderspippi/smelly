Control smelly from scripts
----------------------------

.. highlight:: sh

|smelly| can be controlled from scripts or the shell prompt. You can open new
windows, send arbitrary text input to any window, change the title of windows
and tabs, etc.

Let's walk through a few examples of controlling |smelly|.


Tutorial
------------

Start by running |smelly| as::

    smelly -o allow_remote_control=yes -o enabled_layouts=tall

In order for control to work, :opt:`allow_remote_control` or
:opt:`remote_control_password` must be enabled in :file:`smelly.conf`. Here we
turn it on explicitly at the command line.

Now, in the new |smelly| window, enter the command::

    smelly @ launch --title Output --keep-focus cat

This will open a new window, running the :program:`cat` program that will appear
next to the current window.

Let's send some text to this new window::

    smelly @ send-text --match cmdline:cat Hello, World

This will make ``Hello, World`` show up in the window running the :program:`cat`
program. The :option:`smelly @ send-text --match` option is very powerful, it
allows selecting windows by their titles, the command line of the program
running in the window, the working directory of the program running in the
window, etc. See :ref:`smelly @ send-text --help <at-send-text>` for details.

More usefully, you can pipe the output of a command running in one window to
another window, for example::

    ls | smelly @ send-text --match 'title:^Output' --stdin

This will show the output of :program:`ls` in the output window instead of the
current window. You can use this technique to, for example, show the output of
running :program:`make` in your editor in a different window. The possibilities
are endless.

You can even have things you type show up in a different window. Run::

    smelly @ send-text --match 'title:^Output' --stdin

And type some text, it will show up in the output window, instead of the current
window. Type :kbd:`Ctrl+D` when you are ready to stop.

Now, let's open a new tab::

   smelly @ launch --type=tab --tab-title "My Tab" --keep-focus bash

This will open a new tab running the bash shell with the title "My Tab".
We can change the title of the tab to "New Title" with::

   smelly @ set-tab-title --match 'title:^My' New Title

Let's change the title of the current tab::

   smelly @ set-tab-title Master Tab

Now lets switch to the newly opened tab::

   smelly @ focus-tab --match 'title:^New'

Similarly, to focus the previously opened output window (which will also switch
back to the old tab, automatically)::

   smelly @ focus-window --match 'title:^Output'

You can get a listing of available tabs and windows, by running::

   smelly @ ls

This outputs a tree of data in JSON format. The top level of the tree is all
:term:`OS windows <os_window>`. Each OS window has an id and a list of
:term:`tabs <tab>`. Each tab has its own id, a title and a list of :term:`smelly
windows <window>`. Each window has an id, title, current working directory,
process id (PID) and command-line of the process running in the window. You can
use this information with :option:`smelly @ focus-window --match` to control
individual windows.

As you can see, it is very easy to control |smelly| using the ``smelly @``
messaging system. This tutorial touches only the surface of what is possible.
See ``smelly @ --help`` for more details.

In the example's above, ``smelly @`` messaging works only when run
inside a |smelly| window, not anywhere. But, within a |smelly| window it even
works over SSH. If you want to control |smelly| from programs/scripts not running
inside a |smelly| window, see the section on :ref:`using a socket for remote control <rc_via_socket>`
below.


Note that if all you want to do is run a single |smelly| "daemon" and have
subsequent |smelly| invocations appear as new top-level windows, you can use the
simpler :option:`smelly --single-instance` option, see ``smelly --help`` for that.


.. _rc_via_socket:

Remote control via a socket
--------------------------------
First, start |smelly| as::

    smelly -o allow_remote_control=yes --listen-on unix:/tmp/mysmelly

The :option:`smelly --listen-on` option tells |smelly| to listen for control
messages at the specified UNIX-domain socket. See ``smelly --help`` for details.
Now you can control this instance of |smelly| using the :option:`smelly @ --to`
command line argument to ``smelly @``. For example::

    smelly @ --to unix:/tmp/mysmelly ls


The builtin smelly shell
--------------------------

You can explore the |smelly| command language more easily using the builtin
|smelly| shell. Run ``smelly @`` with no arguments and you will be dropped into
the |smelly| shell with completion for |smelly| command names and options.

You can even open the |smelly| shell inside a running |smelly| using a simple
keyboard shortcut (:sc:`smelly_shell` by default).

.. note:: This has the added advantage that you don't need to use
   :opt:`allow_remote_control` to make it work.


Allowing only some windows to control smelly
----------------------------------------------

If you do not want to allow all programs running in |smelly| to control it, you
can selectively enable remote control for only some |smelly| windows. Simply
create a shortcut such as::

    map ctrl+k launch --allow-remote-control some_program

Then programs running in windows created with that shortcut can use ``smelly @``
to control smelly. Note that any program with the right level of permissions can
still write to the pipes of any other program on the same computer and therefore
can control |smelly|. It can, however, be useful to block programs running on
other computers (for example, over SSH) or as other users.

.. note:: You don't need :opt:`allow_remote_control` to make this work as it is
   limited to only programs running in that specific window. Be careful with
   what programs you run in such windows, since they can effectively control
   smelly, as if you were running with :opt:`allow_remote_control` turned on.

    You can further restrict what is allowed in these windows by using
    :option:`smelly @ launch --remote-control-password`.


Fine grained permissions for remote control
----------------------------------------------

.. versionadded:: 0.26.0

The :opt:`allow_remote_control` option discussed so far is a blunt
instrument, granting the ability to any program running on your computer
or even on remote computers via SSH the ability to use remote control.

You can instead define remote control passwords that can be used to grant
different levels of control to different places. You can even write your
own script to decide which remote control requests are allowed. This is
done using the :opt:`remote_control_password` option in :file:`smelly.conf`.
Set :opt:`allow_remote_control` to :code:`password` to use this feature.
Let's see some examples:

.. code-block:: conf

   remote_control_password "control colors" get-colors set-colors

Now, using this password, you can, in scripts run the command::

    smelly @ --password="control colors" set-colors background=red

Any script with access to the password can now change colors in smelly using
remote control, but only that and nothing else. You can even supply the
password via the :envvar:`smelly_RC_PASSWORD` environment variable, or the
file :file:`~/.config/smelly/rc-password` to avoid having to type it repeatedly.
See :option:`smelly @ --password-file` and :option:`smelly @ --password-env`.

The :opt:`remote_control_password` can be specified multiple times to create
different passwords with different capabilities. Run the following to get a
list of all action names::

    smelly @ --help

You can even use glob patterns to match action names, for example:

.. code-block:: conf

   remote_control_password "control colors" *-colors

If no action names are specified, all actions are allowed.

If ``smelly @`` is run with a password that is not present in
:file:`smelly.conf`, then smelly will interactively prompt the user to allow or
disallow the remote control request. The user can choose to allow or disallow
either just that request or all requests using that password. The user's
decision is remembered for the duration of that smelly instance.

.. note::
   For password based authentication to work over SSH, you must pass the
   :envvar:`smelly_PUBLIC_KEY` environment variable to the remote host. The
   :doc:`ssh kitten <wellies/ssh>` does this for you automatically. When
   using a password, :ref:`rc_crypto` is used to ensure the password
   is kept secure. This does mean that using password based authentication
   is slower as the entire command is encrypted before transmission. This
   can be noticeable when using a command like ``smelly @ set-background-image``
   which transmits large amounts of image data. Also, the clock on the remote
   system must match (within a few minutes) the clock on the local system.
   smelly uses a time based nonce to minimise the potential for replay attacks.

.. _rc_custom_auth:

Customizing authorization with your own program
____________________________________________________________

If the ability to control access by action names is not fine grained enough,
you can define your own Python script to examine every remote control command
and allow/disallow it. To do so create a file in the smelly configuration
directory, :file:`~/.config/smelly/my_rc_auth.py` and add the following
to :file:`smelly.conf`:

.. code-block:: conf

    remote_control_password "testing custom auth" my_rc_auth.py

:file:`my_rc_auth.py` should define a :code:`is_cmd_allowed` function
as shown below:

.. code-block:: py

    def is_cmd_allowed(pcmd, window, from_socket, extra_data):
        cmd_name = pcmd['cmd']  # the name of the command
        cmd_payload = pcmd['payload']  # the arguments to the command
        # examine the cmd_name and cmd_payload and return True to allow
        # the command or False to disallow it. Return None to have no
        # effect on the command.

        # The command payload will vary from command to command, see
        # the rc protocol docs for details. Below is an example of
        # restricting the launch command to allow only running the
        # default shell.

        if cmd_name != 'launch':
            return None
        if cmd_payload.get('args') or cmd_payload.get('env') or cmd_payload.get('copy_cmdline') or cmd_payload.get('copy_env'):
            return False
        # prints in this function go to the parent smelly process STDOUT
        print('Allowing launch command:', cmd_payload)
        return True


.. _rc_mapping:

Mapping key presses to remote control commands
--------------------------------------------------

If you wish to trigger a remote control command easily with just a keypress,
you can map it in :file:`smelly.conf`. For example::

    map f1 remote_control set-spacing margin=30

Then pressing the :kbd:`F1` key will set the active window margins to
:code:`30`. The syntax for what follows :ac:`remote_control` is exactly the same
as the syntax for what follows :code:`smelly @` above.

If you wish to ignore errors from the command, prefix the command with an
``!``. For example, the following will not return an error when no windows
are matched::

    map f1 remote_control !focus-window --match XXXXXX

.. note:: You do not need :opt:`allow_remote_control` to use these mappings,
   as they are not actual remote programs, but are simply a way to resuse the
   remote control infrastructure via keybings.


Broadcasting what you type to all smelly windows
--------------------------------------------------

As a simple illustration of the power of remote control, lets
have what we type sent to all open smelly windows. To do that define the
following mapping in :file:`smelly.conf`::

    map f1 launch --allow-remote-control smelly +kitten broadcast

Now press :kbd:`F1` and start typing, what you type will be sent to all windows,
live, as you type it.


The remote control protocol
-----------------------------------------------

If you wish to develop your own client to talk to |smelly|, you can use the
:doc:`remote control protocol specification <rc_protocol>`. Note that there
is a statically compiled, standalone executable, ``kitten`` available that
can be used as a remote control client on any UNIX like computer. This can be
downloaded and used directly from the `smelly releases
<https://github.com/backbiter-no/smelly/releases>`__ page::

    kitten @ --help


.. _search_syntax:

Matching windows and tabs
----------------------------

Many remote control operations operate on windows or tabs. To select these, the
:code:`--match` option is often used. This allows matching using various
sophisticated criteria such as title, ids, cmdlines, etc. These criteria are
expressions of the form :code:`field:query`. Where :italic:`field` is the field
against which to match and :italic:`query` is the expression to match. They can
be further combined using Boolean operators, best illustrated with some
examples::

    title:"My special window" or id:43
    title:bash and env:USER=anders
    not id:1
    (id:2 or id:3) and title:something

.. toctree::
   :hidden:

   rc_protocol

.. include:: generated/cli-smelly-at.rst
