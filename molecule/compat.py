# -*- coding: utf-8 -*-
#    Molecule Python 2.6/3.x compatibility module
#    Copyright (C) 2010 Fabio Erculiani
#
#    Copyright 1998-2004 Gentoo Foundation
#    # $Id: output.py 4906 2006-11-01 23:55:29Z zmedico $
#    Copyright (C) 2007-2008 Fabio Erculiani
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
import sys

def get_stringtype():
    """
    Return generic string type for usage in isinstance().
    On Python 2.x, it returns basestring while on Python 3.x it returns
    (str, bytes,)
    """
    if sys.hexversion >= 0x3000000:
        return (str, bytes,)
    else:
        return (basestring,)

def isstring(obj):
    """
    Return whether obj is a string (unicode or raw).

    @param obj: Python object
    @type obj: Python object
    @return: True, if object is string
    @rtype: bool
    """
    if sys.hexversion >= 0x3000000:
        return isinstance(obj, (str, bytes))
    else:
        return isinstance(obj, basestring)

def isunicode(obj):
    """
    Return whether obj is a unicode.

    @param obj: Python object
    @type obj: Python object
    @return: True, if object is unicode
    @rtype: bool
    """
    if sys.hexversion >= 0x3000000:
        return isinstance(obj, str)
    else:
        return isinstance(obj, unicode)

def israwstring(obj):
    if sys.hexversion >= 0x3000000:
        return isinstance(obj, bytes)
    else:
        return isinstance(obj, str)

def get_gettext_kwargs():
    if sys.hexversion >= 0x3000000:
        return {'str': True}
    else:
        return {'unicode': True}

def convert_to_unicode(obj, enctype = 'raw_unicode_escape'):
    """
    Convert generic string to unicode format, this function supports both
    Python 2.x and Python 3.x unicode bullshit.

    @param obj: generic string object
    @type obj: string
    @return: unicode string object
    @rtype: unicode object
    """

    # None support
    if obj is None:
        if sys.hexversion >= 0x3000000:
            return "None"
        else:
            return u"None"

    # int support
    if isinstance(obj, int):
        if sys.hexversion >= 0x3000000:
            return str(obj)
        else:
            return unicode(obj)

    # buffer support
    if isinstance(obj, get_buffer()):
        if sys.hexversion >= 0x3000000:
            return str(obj.tobytes(), enctype)
        else:
            return unicode(obj, enctype)

    # string/unicode support
    if isunicode(obj):
        return obj
    if hasattr(obj, 'decode'):
        return obj.decode(enctype)
    else:
        if sys.hexversion >= 0x3000000:
            return str(obj, enctype)
        else:
            return unicode(obj, enctype)

def convert_to_rawstring(obj, from_enctype = 'raw_unicode_escape'):
    """
    Convert generic string to raw string (str for Python 2.x or bytes for
    Python 3.x).

    @param obj: input string
    @type obj: string object
    @keyword from_enctype: encoding which string is using
    @type from_enctype: string
    @return: raw string
    @rtype: bytes
    """
    if obj is None:
        return convert_to_rawstring("None")
    if isnumber(obj):
        if sys.hexversion >= 0x3000000:
            return bytes(str(obj), from_enctype)
        else:
            return str(obj)
    if isinstance(obj, get_buffer()):
        if sys.hexversion >= 0x3000000:
            return obj.tobytes()
        else:
            return str(obj)
    if not isunicode(obj):
        return obj
    return obj.encode(from_enctype)

def get_buffer():
    """
    Return generic buffer object (supporting both Python 2.x and Python 3.x)
    """
    if sys.hexversion >= 0x3000000:
        return memoryview
    else:
        return buffer

def isfileobj(obj):
    """
    Return whether obj is a file object
    """
    if sys.hexversion >= 0x3000000:
        import io
        return isinstance(obj, io.IOBase)
    else:
        return isinstance(obj, file)

def isnumber(obj):
    """
    Return whether obj is an int, long object.
    """
    if sys.hexversion >= 0x3000000:
        return isinstance(obj, int)
    else:
        return isinstance(obj, (int, long,))
