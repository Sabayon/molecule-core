# -*- coding: utf-8 -*-
#    Molecule Disc Image builder for Sabayon Linux
#    Copyright (C) 2009 Fabio Erculiani
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

import os
from molecule.compat import convert_to_unicode
import molecule.utils

class GenericSpecFunctions(object):

    def ne_string(self, x):
        return x, 'raw_unicode_escape'

    def ne_list(self, x):
        return x

    def always_valid(self, *args):
        return True

    def valid_path(self, x):
        return os.path.lexists(x)

    def valid_file(self, x):
        return os.path.isfile(x)

    def valid_dir(self, x):
        return os.path.isdir(x)

    def ve_string_stripper(self, x):
        return convert_to_unicode(x).strip()

    def ve_string_splitter(self, x):
        return convert_to_unicode(x).strip().split()

    def valid_exec(self, x):
        molecule.utils.is_exec_available(x)
        return x

    def valid_exec_first_list_item(self, x):
        if not x:
            return False
        myx = x[0]
        molecule.utils.is_exec_available(myx)
        return True

    def valid_ascii(self, x):
        try:
            x = str(x)
            return x
        except (UnicodeDecodeError, UnicodeEncodeError,):
            return ''

    def valid_path_string(self, x):
        try:
            os.path.split(x)
        except OSError:
            return False
        return True

    def valid_path_string_first_list_item(self, x):
        if not x:
            return False
        myx = x[0]
        try:
            os.path.split(myx)
        except OSError:
            return False
        return True

    def valid_comma_sep_list(self, x):
        return [y.strip() for y in \
            convert_to_unicode(x).split(",") if y.strip()]

    def valid_path_list(self, x):
        return [y.strip() for y in \
            convert_to_unicode(x).split(",") if \
                self.valid_path_string(y) and y.strip()]

class GenericExecutionStep:

    """
    This class implements a single Molecule Runner step (for example: something
    that copy a chroot from src to dest or generates an ISO image off
    a directory.
    """

    def __init__(self, spec_path, metadata):
        import molecule.settings
        import molecule.output
        self._output = molecule.output.Output()
        self._config = molecule.settings.Configuration()
        self.spec_path = spec_path
        self.metadata = metadata
        self.spec_name = os.path.basename(self.spec_path)
        self._export_generic_info()

    def _export_generic_info(self):
        os.environ['RELEASE_STRING'] = self.metadata.get('release_string', '')
        os.environ['RELEASE_VERSION'] = self.metadata.get('release_version', '')
        os.environ['RELEASE_DESC'] = self.metadata.get('release_desc', '')
        os.environ['PRECHROOT'] = self.metadata.get('prechroot', '')

    def setup(self):
        """
        Execution step setup hook.
        """
        pass

    def pre_run(self):
        """
        Pre-run execution hook.
        """
        raise NotImplementedError()

    def run(self):
        """
        Run execution hook.
        """
        raise NotImplementedError()

    def post_run(self):
        """
        Post-run execution hook.
        """
        raise NotImplementedError()

    def kill(self, success = True):
        """
        Kill execution hook.
        """
        raise NotImplementedError()


class GenericSpec(GenericSpecFunctions):

    EXECUTION_STRATEGY_KEY = "execution_strategy"

    # Molecule Plugin factory support
    BASE_PLUGIN_API_VERSION = 0

    @staticmethod
    def execution_strategy():
        """
        Return a string that describes the supported execution strategy.
        Such as "remaster", "livecd", etc.

        @return: execution strategy string id
        @rtype: string
        """
        raise NotImplementedError()

    def vital_parameters(self):
        """
        Return a list of vital .spec file parameters

        @return: list of vital .spec file parameters
        @rtype: list
        """
        raise NotImplementedError()

    def parser_data_path(self):
        """
        Return a dictionary containing parameter names as key and
        dict containing keys 've' and 'cb' which values are three
        callable functions that respectively do value extraction (ve),
        value verification (cb) and value modding (mod).

        @return: data path dictionary (see ChrootSpec code for more info)
        @rtype: dict
        """
        raise NotImplementedError()

    def get_execution_steps(self):
        """
        Return a list of GenericExecutionStep classes that will be initialized
        and executed by molecule.handlers.Runner
        """
        raise NotImplementedError()
