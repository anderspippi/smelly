#!/usr/bin/env python
# License: GPLv3 Copyright: 2019, anders Goyal <anders at backbiter-no.net>

import re
from typing import Any, Generator, List, Type

from .cli_stub import HintsCLIOptions
from .typing import MarkType


def mark(text: str, args: HintsCLIOptions, Mark: Type[MarkType],
         extra_cli_args: List[str],
         *a: Any) -> Generator[MarkType, None, None]:
    idx = 0
    found_start_line = False
    for m in re.finditer(r'(?m)^.+$', text):
        start, end = m.span()
        line = text[start:end].replace('\0', '').replace('\n', '')
        if line == ' ':
            found_start_line = True
            continue
        if line.startswith(': '):
            yield Mark(idx, start, end, line, {'index': idx})
            idx += 1
        elif found_start_line:
            # skip this line incrementing the index
            idx += 1
