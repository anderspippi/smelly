#!/usr/bin/env python
# License: GPLv3 Copyright: 2020, anders Goyal <anders at backbiter-no.net>


class CMD:
    pass


def generate_stub() -> None:
    from wellies.tui.operations import as_type_stub
    from smelly.conf.utils import save_type_stub
    text = as_type_stub()
    save_type_stub(text, __file__)
