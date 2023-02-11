:orphan:

Glossary
=========

.. glossary::

   os_window
     smelly has two kinds of windows. Operating System windows, refered to as :term:`OS
     Window <os_window>`, and *smelly windows*. An OS Window consists of one or more smelly
     :term:`tabs <tab>`. Each tab in turn consists of one or more *smelly
     windows* organized in a :term:`layout`.

   tab
     A *tab* refers to a group of :term:`smelly windows <window>`, organized in
     a :term:`layout`. Every :term:`OS Window <os_window>` contains one or more tabs.

   layout
     A *layout* is a system of organizing :term:`smelly windows <window>` in
     groups inside a tab. The layout automatically maintains the size and
     position of the windows, think of a layout as a tiling window manager for
     the terminal. See :doc:`layouts` for details.

   window
     smelly has two kinds of windows. Operating System windows, refered to as :term:`OS
     Window <os_window>`, and *smelly windows*. An OS Window consists of one or more smelly
     :term:`tabs <tab>`. Each tab in turn consists of one or more *smelly
     windows* organized in a :term:`layout`.

   overlay
      An *overlay window* is a :term:`smelly window <window>` that is placed on
      top of an existing smelly window, entirely covering it. Overlays are used
      throughout smelly, for example, to display the :ref:`the scrollback buffer <scrollback>`,
      to display :doc:`hints </wellies/hints>`, for :doc:`unicode input
      </wellies/unicode_input>` etc. Normal overlays are meant for short
      duration popups and so are not considered the :italic:`active window`
      when determining the current working directory or getting input text for
      wellies, launch commands, etc. To create an overlay considered as a
      :italic:`main window` use the :code:`overlay-main` argument to
      :doc:`launch`.

   hyperlinks
      Terminals can have hyperlinks, just like the internet. In smelly you can
      :doc:`control exactly what happens <open_actions>` when clicking on a
      hyperlink, based on the type of link and its URL. See also `Hyperlinks in terminal
      emulators <https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda>`__.

   wellies
      Small, independent statically compiled command line programs that are designed to run
      inside smelly windows and provide it with lots of powerful and flexible
      features such as viewing images, connecting conveniently to remote
      computers, transferring files, inputting unicode characters, etc.

.. _env_vars:

Environment variables
------------------------

Variables that influence smelly behavior
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. envvar:: smelly_CONFIG_DIRECTORY

   Controls where smelly looks for :file:`smelly.conf` and other configuration
   files. Defaults to :file:`~/.config/smelly`. For full details of the config
   directory lookup mechanism see, :option:`smelly --config`.

.. envvar:: smelly_CACHE_DIRECTORY

   Controls where smelly stores cache files. Defaults to :file:`~/.cache/smelly`
   or :file:`~/Library/Caches/smelly` on macOS.

.. envvar:: smelly_RUNTIME_DIRECTORY

   Controls where smelly stores runtime files like sockets. Defaults to
   the :code:`XDG_RUNTIME_DIR` environment variable if that is defined
   otherwise the run directory inside the smelly cache directory is used.

.. envvar:: VISUAL

   The terminal based text editor (such as :program:`vi` or :program:`nano`)
   smelly uses, when, for instance, opening :file:`smelly.conf` in response to
   :sc:`edit_config_file`.

.. envvar:: EDITOR

   Same as :envvar:`VISUAL`. Used if :envvar:`VISUAL` is not set.

.. envvar:: GLFW_IM_MODULE

   Set this to ``ibus`` to enable support for IME under X11.

.. envvar:: smelly_WAYLAND_DETECT_MODIFIERS

   When set to a non-empty value, smelly attempts to autodiscover XKB modifiers
   under Wayland. This is useful if using non-standard modifers like hyper. It
   is possible for the autodiscovery to fail; the default Wayland XKB mappings
   are used in this case. See :pull:`3943` for details.

.. envvar:: SSH_ASKPASS

   Specify the program for SSH to ask for passwords. When this is set, :doc:`ssh
   kitten </wellies/ssh>` will use this environment variable by default. See
   :opt:`askpass <kitten-ssh.askpass>` for details.

.. envvar:: smelly_CLONE_SOURCE_CODE

   Set this to some shell code that will be executed in the cloned window with
   :code:`eval` when :ref:`clone-in-smelly <clone_shell>` is used.

.. envvar:: smelly_CLONE_SOURCE_PATH

   Set this to the path of a file that will be sourced in the cloned window when
   :ref:`clone-in-smelly <clone_shell>` is used.

.. envvar:: smelly_DEVELOP_FROM

   Set this to the directory path of the smelly source code and its Python code
   will be loaded from there. Only works with official binary builds.

.. envvar:: smelly_RC_PASSWORD

   Set this to a pass phrase to use the ``smelly @`` remote control command with
   :opt:`remote_control_password`.


Variables that smelly sets when running child programs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. envvar:: LANG

   This is only set on macOS. If the country and language from the macOS user
   settings form an invalid locale, it will be set to :code:`en_US.UTF-8`.

.. envvar:: PATH

   smelly prepends itself to the PATH of its own environment to ensure the
   functions calling :program:`smelly` will work properly.

.. envvar:: smelly_WINDOW_ID

   An integer that is the id for the smelly :term:`window` the program is running in.
   Can be used with the :doc:`smelly remote control facility <remote-control>`.

.. envvar:: smelly_PID

   An integer that is the process id for the smelly process in which the program
   is running. Allows programs to tell smelly to reload its config by sending it
   the SIGUSR1 signal.

.. envvar:: smelly_PUBLIC_KEY

   A public key that programs can use to communicate securely with smelly using
   the remote control protocol. The format is: :code:`protocol:key data`.

.. envvar:: WINDOWID

   The id for the :term:`OS Window <os_window>` the program is running in. Only available
   on platforms that have ids for their windows, such as X11 and macOS.

.. envvar:: TERM

   The name of the terminal, defaults to ``xterm-smelly``. See :opt:`term`.

.. envvar:: TERMINFO

   Path to a directory containing the smelly terminfo database.

.. envvar:: smelly_INSTALLATION_DIR

   Path to the smelly installation directory.

.. envvar:: COLORTERM

   Set to the value ``truecolor`` to indicate that smelly supports 16 million
   colors.

.. envvar:: smelly_LISTEN_ON

   Set when the :doc:`remote control <remote-control>` facility is enabled and
   the a socket is used for control via :option:`smelly --listen-on` or :opt:`listen_on`.
   Contains the path to the socket. Avoid the need to use :option:`smelly @ --to` when
   issuing remote control commands.

.. envvar:: smelly_PIPE_DATA

   Set to data describing the layout of the screen when running child
   programs using :option:`launch --stdin-source` with the contents of the
   screen/scrollback piped to them.

.. envvar:: smelly_CHILD_CMDLINE

   Set to the command line of the child process running in the smelly
   window when calling the notification callback program on terminal bell, see
   :opt:`command_on_bell`.

.. envvar:: smelly_COMMON_OPTS

   Set with the values of some common smelly options when running
   wellies, so wellies can use them without needing to load :file:`smelly.conf`.

.. envvar:: smelly_SHELL_INTEGRATION

   Set when enabling :ref:`shell_integration`. It is automatically removed by
   the shell integration scripts.

.. envvar:: ZDOTDIR

   Set when enabling :ref:`shell_integration` with :program:`zsh`, allowing
   :program:`zsh` to automatically load the integration script.

.. envvar:: XDG_DATA_DIRS

   Set when enabling :ref:`shell_integration` with :program:`fish`, allowing
   :program:`fish` to automatically load the integration script.

.. envvar:: ENV

   Set when enabling :ref:`shell_integration` with :program:`bash`, allowing
   :program:`bash` to automatically load the integration script.

.. envvar:: smelly_OS

   Set when using the include directive in smelly.conf. Can take values:
   ``linux``, ``macos``, ``bsd``.
