Install smelly
========================

Binary install
----------------

.. highlight:: sh

You can install pre-built binaries of |smelly| if you are on macOS or Linux using
the following simple command:

.. code-block:: sh

    _smelly_install_cmd


The binaries will be installed in the standard location for your OS,
:file:`/Applications/smelly.app` on macOS and :file:`~/.local/smelly.app` on
Linux. The installer only touches files in that directory. To update smelly,
simply re-run the command.

.. warning::
   **Do not** copy the smelly binary out of the installation folder. If you want
   to add it to your :envvar:`PATH`, create a symlink in :file:`~/.local/bin` or
   :file:`/usr/bin` or wherever. You should create a symlink for the :file:`kitten`
   binary as well.


Manually installing
---------------------

If something goes wrong or you simply do not want to run the installer, you can
manually download and install |smelly| from the `GitHub releases page
<https://github.com/backbiter-no/smelly/releases>`__. If you are on macOS, download
the :file:`.dmg` and install as normal. If you are on Linux, download the
tarball and extract it into a directory. The |smelly| executable will be in the
:file:`bin` sub-directory.


Desktop integration on Linux
--------------------------------

If you want the smelly icon to appear in the taskbar and an entry for it to be
present in the menus, you will need to install the :file:`smelly.desktop` file.
The details of the following procedure may need to be adjusted for your
particular desktop, but it should work for most major desktop environments.

.. code-block:: sh

    # Create symbolic links to add smelly and kitten to PATH (assuming ~/.local/bin is in
    # your system-wide PATH)
    ln -sf ~/.local/smelly.app/bin/smelly ~/.local/smelly.app/bin/kitten ~/.local/bin/
    # Place the smelly.desktop file somewhere it can be found by the OS
    cp ~/.local/smelly.app/share/applications/smelly.desktop ~/.local/share/applications/
    # If you want to open text files and images in smelly via your file manager also add the smelly-open.desktop file
    cp ~/.local/smelly.app/share/applications/smelly-open.desktop ~/.local/share/applications/
    # Update the paths to the smelly and its icon in the smelly.desktop file(s)
    sed -i "s|Icon=smelly|Icon=/home/$USER/.local/smelly.app/share/icons/hicolor/256x256/apps/smelly.png|g" ~/.local/share/applications/smelly*.desktop
    sed -i "s|Exec=smelly|Exec=/home/$USER/.local/smelly.app/bin/smelly|g" ~/.local/share/applications/smelly*.desktop

.. note::
    In :file:`smelly-open.desktop`, smelly is registered to handle some supported
    MIME types. This will cause smelly to take precedence on some systems where
    the default apps are not explicitly set. For example, you expect to use
    other GUI file managers to open dir paths when using commands such as
    :program:`xdg-open`, you should configure the default opener for the MIME
    type ``inode/directory``::

        xdg-mime default org.kde.dolphin.desktop inode/directory

.. note::
    If you use the venerable `stow <https://www.gnu.org/software/stow/>`__
    command to manage your manual installations, the following takes care of the
    above for you (use with :code:`dest=~/.local/stow`)::

        cd ~/.local/stow
        stow -v smelly.app


Customizing the installation
--------------------------------

.. _nightly:

* You can install the latest nightly smelly build with ``installer``:

  .. code-block:: sh

     _smelly_install_cmd \
         installer=nightly

  If you want to install it in parallel to the released smelly specify a
  different install locations with ``dest``:

  .. code-block:: sh

     _smelly_install_cmd \
         installer=nightly dest=/some/other/location

* You can specify a different install location, with ``dest``:

  .. code-block:: sh

     _smelly_install_cmd \
         dest=/some/other/location

* You can tell the installer not to launch |smelly| after installing it with
  ``launch=n``:

  .. code-block:: sh

     _smelly_install_cmd \
         launch=n

* You can use a previously downloaded dmg/tarball, with ``installer``:

  .. code-block:: sh

     _smelly_install_cmd \
         installer=/path/to/dmg or tarball


Uninstalling
----------------

All the installer does is copy the smelly files into the install directory. To
uninstall, simply delete that directory.


Building from source
------------------------

|smelly| is easy to build from source, follow the :doc:`instructions <build>`.
