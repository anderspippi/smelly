#!/usr/bin/env python
# License: GPLv3 Copyright: 2020, anders Goyal <anders at backbiter-no.net>


from typing import TYPE_CHECKING, Optional

from smelly.fast_data_types import focus_os_window

from .base import MATCH_WINDOW_OPTION, ArgsType, Boss, PayloadGetType, PayloadType, RCOptions, RemoteCommand, ResponseType, Window

if TYPE_CHECKING:
    from smelly.cli_stub import FocusWindowRCOptions as CLIOptions


class FocusWindow(RemoteCommand):
    protocol_spec = __doc__ = '''
    match/str: The window to focus
    '''

    short_desc = 'Focus the specified window'
    desc = 'Focus the specified window, if no window is specified, focus the window this command is run inside.'
    options_spec = (
        MATCH_WINDOW_OPTION
        + '''\n\n
--no-response
type=bool-set
default=false
Don't wait for a response from smelly. This means that even if no matching window is found,
the command will exit with a success code.
'''
    )

    def message_to_smelly(self, global_opts: RCOptions, opts: 'CLIOptions', args: ArgsType) -> PayloadType:
        return {'match': opts.match}

    def response_from_smelly(self, boss: Boss, window: Optional[Window], payload_get: PayloadGetType) -> ResponseType:
        for window in self.windows_for_match_payload(boss, window, payload_get):
            if window:
                os_window_id = boss.set_active_window(window)
                if os_window_id:
                    focus_os_window(os_window_id, True)
                break
        return None


focus_window = FocusWindow()
