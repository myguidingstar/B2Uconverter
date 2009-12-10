""" Python Character Mapping Codec cp1252 (Microsoft - West European languages)
    Copyright (c) 2008-2009  Jean Christophe André <jcandre@hanoilug.org>
    License: GNU Lesser General Public License version 2.1
    To enable this encoding, move this file into /usr/lib/python2.5/encodings/
"""

def _create_cp1252_to_unicode_table():
    cp1252_begin = ''.join(map(unichr,range(0,0x80)))
    cp1252_specials = (
        u'\u20ac'   #  0x80 -> EURO SIGN
        u'\x81'     #  0x81
        u'\u201a'   #  0x82 -> SINGLE LOW-9 QUOTATION MARK
        u'\u0192'   #  0x83 -> LATIN SMALL LETTER F WITH HOOK
        u'\u201e'   #  0x84 -> DOUBLE LOW-9 QUOTATION MARK
        u'\u2026'   #  0x85 -> HORIZONTAL ELLIPSIS
        u'\u2020'   #  0x86 -> DAGGER
        u'\u2021'   #  0x87 -> DOUBLE DAGGER
        u'\u02c6'   #  0x88 -> MODIFIER LETTER CIRCUMFLEX ACCENT
        u'\u2030'   #  0x89 -> PER MILLE SIGN
        u'\u0160'   #  0x8A -> LATIN CAPITAL LETTER S WITH CARON
        u'\u2039'   #  0x8B -> SINGLE LEFT-POINTING ANGLE QUOTATION MARK
        u'\u0152'   #  0x8C -> LATIN CAPITAL LIGATURE OE
        u'\x8D'     #  0x8D
        u'\u017d'   #  0x8E -> LATIN CAPITAL LETTER Z WITH CARON
        u'\x8F'     #  0x8F
        u'\x90'     #  0x90
        u'\u2018'   #  0x91 -> LEFT SINGLE QUOTATION MARK
        u'\u2019'   #  0x92 -> RIGHT SINGLE QUOTATION MARK
        u'\u201c'   #  0x93 -> LEFT DOUBLE QUOTATION MARK
        u'\u201d'   #  0x94 -> RIGHT DOUBLE QUOTATION MARK
        u'\u2022'   #  0x95 -> BULLET
        u'\u2013'   #  0x96 -> EN DASH
        u'\u2014'   #  0x97 -> EM DASH
        u'\u02dc'   #  0x98 -> SMALL TILDE
        u'\u2122'   #  0x99 -> TRADE MARK SIGN
        u'\u0161'   #  0x9A -> LATIN SMALL LETTER S WITH CARON
        u'\u203a'   #  0x9B -> SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
        u'\u0153'   #  0x9C -> LATIN SMALL LIGATURE OE
        u'\x9D'     #  0x9D
        u'\u017e'   #  0x9E -> LATIN SMALL LETTER Z WITH CARON
        u'\u0178'   #  0x9F -> LATIN CAPITAL LETTER Y WITH DIAERESIS
    )
    cp1252_end = ''.join(map(unichr,range(0xA0,0x100)))
    return cp1252_begin + cp1252_specials + cp1252_end

cp1252_decoding_table = _create_cp1252_to_unicode_table()

