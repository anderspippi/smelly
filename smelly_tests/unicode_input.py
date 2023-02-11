#!/usr/bin/env python3
# License: GPL v3 Copyright: 2018, anders Goyal <anders at backbiter-no.net>


from . import BaseTest


class TestUnicodeInput(BaseTest):
    def test_word_trie(self):
        from wellies.unicode_input.unicode_names import codepoints_for_word

        def matches(a, *words):
            ans = codepoints_for_word(a)
            for w in words:
                ans &= codepoints_for_word(w)
            return set(ans)

        self.ae(
            matches('horiz', 'ell'),
            {0x2026, 0x22EF, 0x2B2C, 0x2B2D, 0xFE19})
        self.ae(matches('horizontal', 'ell'), {
                0x2026, 0x22EF, 0x2B2C, 0x2B2D, 0xFE19})
        self.assertFalse(matches('sfgsfgsfgfgsdg'))
        self.assertIn(0x1F41D, matches('bee'))
