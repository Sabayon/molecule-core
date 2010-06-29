# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from molecule.compat import get_gettext_kwargs

_LOCALE = None
try:
    import gettext
    import os
    gettext.bindtextdomain('molecule', '/usr/share/locale')
    gettext.textdomain('molecule')
    gettext.install('molecule', *get_gettext_kwargs())
    _ = _

    _LOCALE_FULL = os.getenv('LC_ALL')
    if _LOCALE_FULL == None:
        _LOCALE_FULL = os.getenv('LANG')
    if _LOCALE_FULL == None:
        _LOCALE_FULL = os.getenv('LANGUAGE')

    if _LOCALE_FULL:
        _LOCALE = _LOCALE_FULL.split('.')[0]
        _LOCALE = _LOCALE.split('_')[0]
        _LOCALE = _LOCALE.lower()

except:
    def _(s):
        return s
