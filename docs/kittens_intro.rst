.. _wellies:

Extend with wellies
-----------------------

.. toctree::
   :hidden:
   :glob:

   wellies/icat
   wellies/diff
   wellies/unicode_input
   wellies/themes
   wellies/hints
   wellies/remote_file
   wellies/hyperlinked_grep
   wellies/transfer
   wellies/ssh
   wellies/custom
   wellies/*

|smelly| has a framework for easily creating terminal programs that make use of
its advanced features. These programs are called wellies. They are used both to
add features to |smelly| itself and to create useful standalone programs.
Some prominent wellies:

:doc:`icat <wellies/icat>`
    Display images in the terminal


:doc:`diff <wellies/diff>`
    A fast, side-by-side diff for the terminal with syntax highlighting and
    images


:doc:`Unicode input <wellies/unicode_input>`
    Easily input arbitrary Unicode characters in |smelly| by name or hex code.


:doc:`Hints <wellies/hints>`
    Select and open/paste/insert arbitrary text snippets such as URLs,
    filenames, words, lines, etc. from the terminal screen.


:doc:`Remote file <wellies/remote_file>`
    Edit, open, or download remote files over SSH easily, by simply clicking on
    the filename.


:doc:`Transfer files <wellies/transfer>`
    Transfer files and directories seamlessly and easily from remote machines
    over your existing SSH sessions with a simple command.


:doc:`Hyperlinked grep <wellies/hyperlinked_grep>`
    Search your files using `ripgrep <https://github.com/BurntSushi/ripgrep>`__
    and open the results directly in your favorite editor in the terminal,
    at the line containing the search result, simply by clicking on the result
    you want.


:doc:`Broadcast <wellies/broadcast>`
    Type in one :term:`smelly window <window>` and have it broadcast to all (or a
    subset) of other :term:`smelly windows <window>`.


:doc:`SSH <wellies/ssh>`
    SSH with automatic :ref:`shell integration <shell_integration>`, connection
    re-use for low latency and easy cloning of local shell and editor
    configuration to the remote host.


:doc:`Panel <wellies/panel>`
    Draw a GPU accelerated dock panel on your desktop showing the output from an
    arbitrary terminal program.


:doc:`Clipboard <wellies/clipboard>`
    Copy/paste to the clipboard from shell scripts, even over SSH.

You can also :doc:`Learn to create your own wellies <wellies/custom>`.
