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
import shlex
import stat

from molecule.compat import convert_to_unicode, convert_to_rawstring, is_python3

import molecule.utils


class GenericExecutionStep(object):

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


class GenericSpec(object):

    EXECUTION_STRATEGY_KEY = "execution_strategy"

    # Molecule Plugin factory support
    BASE_PLUGIN_API_VERSION = 1

    def __init__(self, spec_file):
        """
        Object constructor.

        @param spec_file: path to the spec file to be parsed
        @type spec_file: string
        """
        self._spec_file = spec_file

    def _command_splitter(self, string):
        """
        Split a command string into list using shlex.
        """
        x_str = string
        if not is_python3():
            x_str = convert_to_rawstring(x_str)
        return [convert_to_unicode(y) for y in shlex.split(x_str)]

    def _verify_command_arguments(self, args):
        """
        Given an argument list, verify that the first argument
        points to an available executable (in PATH).
        """
        if not args:
            return False
        return molecule.utils.is_exec_available(args[0])

    def _verify_executable_arguments(self, args):
        """
        Given an argument list, verifiy that the first argument
        points to an executable file.
        """
        if not args:
            return False

        exe = args[0]
        if not os.path.isfile(exe):
            return False
        try:
            return os.stat(exe).st_mode & (
                stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except OSError:
            return False

    def _comma_separate(self, string):
        """
        Split a string using "," as delimiter. Filter out empty
        elemets.
        """
        return [x.strip() for x in string.split(",") if x.strip()]

    def _comma_separate_path(self, string):
        """
        Same as _comma_separate() but also filter out invalid paths.
        """
        return [x.strip() for x in string.split(",") \
                    if x.strip() and "\0" not in x]

    def _cast_integer(self, string):
        """
        Try to cast a string into an integer, return None if it fails.
        """
        try:
            return int(string)
        except ValueError:
            return None

    @staticmethod
    def require_super_user():
        """
        Determine whether super user access is required in order to execute
        the given GenericSpec subclass. Default: True. Please override if
        you allow unprivileged user execution.
        """
        return True

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

    def parameters(self):
        """
        Return a dictionary containing parameter names as key and
        dict containing keys 'parser' and 'verifier' which values are three
        callable functions that respectively do value parsing (parser),
        value verification (verifier).

        @return: data path dictionary (see ChrootSpec code for more info)
        @rtype: dict
        """
        raise NotImplementedError()

    def execution_steps(self):
        """
        Return a list of GenericExecutionStep classes that will be initialized
        and executed by molecule.handlers.Runner
        """
        raise NotImplementedError()

    def output(self, metadata):
        """
        Given the parsed metadata as input, execute any kind of logging or
        stdout/stderr push. This method is a no-op.
        """
