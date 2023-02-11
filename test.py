#!./smelly/launcher/smelly +launch
# License: GPL v3 Copyright: 2016, anders Goyal <anders at backbiter-no.net>

import importlib


def main() -> None:
    m = importlib.import_module('smelly_tests.main')
    getattr(m, 'main')()


if __name__ == '__main__':
    main()
