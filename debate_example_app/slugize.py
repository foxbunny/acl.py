#!/usr/env python
# -*- coding: utf-8 -*-

import re
import pdb

TRANS_PAIRS = { 
    'en': {
        u'æ': u'ae',
        u'é': u'e',
    },
    'gr': {
        u'α': u'a',
        u'β': u'b',
        u'γ': u'g',
        u'δ': u'd',
        u'ε': u'e',
        u'ζ': u'z',
        u'η': u'h',
        u'θ': u'8',
        u'ι': u'i',
        u'κ': u'k',
        u'λ': u'l',
        u'μ': u'm',
        u'ν': u'n',
        u'ξ': u'3',
        u'ο': u'o',
        u'π': u'p',
        u'ρ': u'r',
        u'σ': u's',
        u'τ': u't',
        u'υ': u'y',
        u'φ': u'f',
        u'χ': u'x',
        u'ψ': u'ps',
        u'ω': u'w',
        u'ά': u'a',
        u'έ': u'e',
        u'ί': u'i',
        u'ό': u'o',
        u'ύ': u'y',
        u'ή': u'h',
        u'ώ': u'w',
        u'ς': u's',
        u'ϊ': u'i',
        u'ΰ': u'y',
        u'ϋ': u'y',
        u'ΐ': u'i',
    },
    'ru': {
        u'а': u'a',
        u'б': u'b',
        u'в': u'v',
        u'г': u'g',
        u'д': u'd',
        u'е': u'e',
        u'ё': u'io',
        u'ж': u'j',
        u'з': u'z',
        u'и': u'i',
        u'й': u'yi',
        u'к': u'k',
        u'л': u'l',
        u'м': u'm',
        u'н': u'n',
        u'о': u'o',
        u'п': u'p',
        u'р': u'r',
        u'с': u's',
        u'т': u't',
        u'у': u'u',
        u'ф': u'f',
        u'х': u'h',
        u'ц': u'ts',
        u'ч': u'ch',
        u'ш': u'sh',
        u'щ': u'shch',
        u'ъ': u'i',
        u'ы': u'i',
        u'ь': u'i',
        u'э': u'ye',
        u'ю': u'u',
        u'я': u'ya',
        u'ă': u'a',
        u'î': u'i',
        u'ţ': u't',
        u'â': u'a',
        u'ş': u's',
    },
    'uk': {
        u'є': u'ye',
        u'і': u'i',
        u'ї': u'yi',
        u'ґ': u'g',
    },
    'cz': {
        u'č': u'c',
        u'ď': u'd',
        u'ě': u'e',
        u'ň': u'n',
        u'ř': u'r',
        u'š': u's',
        u'ť': u't',
        u'ů': u'u',
        u'ž': u'z',
    },
    'pl': {
        u'ą': u'a',
        u'ć': u'c',
        u'ę': u'e',
        u'ł': u'l',
        u'ń': u'n',
        u'ó': u'o',
        u'ś': u's',
        u'ź': u'z',
        u'ż': u'z',
    },
    'lv': {
        u'ā': u'a',
        u'č': u'c',
        u'ē': u'e',
        u'ģ': u'g',
        u'ī': u'i',
        u'ķ': u'k',
        u'ļ': u'l',
        u'ņ': u'n',
        u'š': u's',
        u'ū': u'u',
        u'ž': u'z',
    },
    'sr': {
        u'а': u'a',
        u'б': u'b',
        u'в': u'v',
        u'г': u'g',
        u'д': u'd',
        u'ђ': u'dj',
        u'е': u'e',
        u'ж': u'j',
        u'з': u'z',
        u'и': u'i',
        u'ј': u'j',
        u'к': u'k',
        u'л': u'l',
        u'љ': u'lj',
        u'м': u'm',
        u'н': u'n',
        u'њ': u'nj',
        u'о': u'o',
        u'п': u'p',
        u'р': u'r',
        u'с': u's',
        u'т': u't',
        u'ћ': u'c',
        u'у': u'u',
        u'ф': u'f',
        u'х': u'h',
        u'ц': u'c',
        u'ч': u'c',
        u'џ': u'dz',
        u'ш': u's',
        u'č': u'c',
        u'ć': u'c',
        u'đ': u'dj',
        u'š': u's',
        u'ž': u'z',
    },
    'tr': {
        u'ç': u'c',
        u'ğ': u'g',
        u'ı': u'i',
        u'İ': u'I',
        u'ö': u'o',
        u'ş': u's',
        u'ü': u'u',
    }}

def transliterate(str, transpairs):
    """Transliterate str based on transpairs pairs of strings

    ``str`` is a unicode string to be parsed.
    ``transpairs`` is a dict containing character pairs

    There is no need to prepend ``(?u)`` to the first character in a character
    pair, as this is done for you by ``transliterate()``.
 
    """
    
    for key in transpairs.keys():
        sourcechar = u'(?u)' + unicode(key)
        translit_re = re.compile(sourcechar, re.UNICODE)
        str = translit_re.sub(unicode(transpairs.get(key, '')), unicode(str))
    return str

def slugize(str, locales=[], exclude_locales=[], spacer='-', max_length=0):
    """Convert ``str`` to a URL-friendly string

    ``str`` is a unicode string to be converted
    ``locales`` is a list of ISO locale codes to use for transliteration
    ``spacer`` is a string to use for replace spaces and interpunction
    ``max_length`` specifies the maximum length of the slug to be returned

    If ``max_length`` is 0, the whole slug is returned.

    Returns a *unicode* string.

    """

    locales = locales if len(locales) else TRANS_PAIRS.keys()

    if exclude_locales:
        for locale in exclude_locales:
            if locale in locales:
                locales.remove(locale)

    str = unicode(str.lower())
    
    for locale in locales:
        str = transliterate(str, TRANS_PAIRS.get(locale, 'en'))

    discard_re = re.compile(r"[\@\!\?\-_,'\";:\.\^#$\%&=+*»«<>„“’‘\(\)\[\]{}\\\/\|]", 
                            re.UNICODE)
    str = discard_re.sub("", str)
    if max_length:
        str = str[0:max_length]
    return spacer.join(str.split())
