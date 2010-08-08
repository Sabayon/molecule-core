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
from molecule.compat import get_stringtype
from molecule.exception import SpecFileError
from molecule.specs.skel import GenericSpec
from molecule.version import VERSION
import molecule.utils

class Constants(dict):

    def __init__(self):
        dict.__init__(self)
        self.load()

    def load(self):
        ETC_DIR = '/etc'
        CONFIG_FILE_NAME = 'molecule.conf'

        mysettings = {
            'config_file': os.path.join(ETC_DIR, CONFIG_FILE_NAME),
        }

        self.clear()
        self.update(mysettings)

class Configuration(dict):

    def __init__(self):
        dict.__init__(self)
        self.Constants = Constants()
        self.load()

    def load(self, mysettings = None):
        if mysettings is None:
            mysettings = {}
        settings = {
            'version': VERSION,
            'chroot_compressor': "/usr/bin/mksquashfs",
            'iso_builder': "/usr/bin/mkisofs",
            'mirror_syncer': "/usr/bin/rsync",
            'chroot_compressor_builtin_args': ["-noappend", "-no-progress"],
            'iso_builder_builtin_args': ["-J", "-R", "-l", "-no-emul-boot",
                "-boot-load-size", "4", "-udf", "-boot-info-table"],
            'mirror_syncer_builtin_args': ["-a", "--delete",
                "--delete-excluded", "--delete-during", "--numeric-ids",
                "--recursive", "-d", "-A", "-H"],
            'chroot_compressor_output_file': "livecd.squashfs",
            'iso_mounter': ["/bin/mount", "-o", "loop,ro", "-t", "iso9660"],
            'iso_umounter': ["/bin/umount"],
            'squash_mounter': ["/bin/mount", "-o", "loop,ro", "-t", "squashfs"],
            'squash_umounter': ["/bin/umount"],
            'pkgs_adder': ["/usr/bin/equo", "install"],
            'pkgs_remover': ["/usr/bin/equo", "remove"],
            'pkgs_updater': ["/usr/bin/equo", "update"],
        }
        self.clear()
        self.update(settings)
        self.update(mysettings)

        paths_to_check = ["chroot_compressor", "iso_builder", "mirror_syncer"]
        for key in paths_to_check:
            molecule.utils.valid_exec_check(self.get(key))


class SpecPreprocessor:

    PREFIX = "%"
    class PreprocessorError(Exception):
        """ Error while preprocessing file """

    def __init__(self, spec_path):
        self.__expanders = {}
        self.__builtin_expanders = {}
        self._spec_path = spec_path
        self._add_builtin_expanders()

    def add_expander(self, statement, expander_callback):
        """
        Add Preprocessor expander.

        @param statement: statement to expand
        @type statement: string
        @param expand_callback: one argument callback that is used to expand
            given line (line is raw format). Line is already pre-parsed and
            contains a valid preprocessor statement that callback can handle.
            Preprocessor callback should raise SpecPreprocessor.PreprocessorError
            if line is malformed.
        @type expander_callback: callable
        @raise KeyError: if expander is already available
        @return: a raw string (containing \n and whatever)
        @rtype: string
        """
        return self._add_expander(statement, expander_callback, builtin = False)

    def _add_expander(self, statement, expander_callback, builtin = False):
        obj = self.__expanders
        if builtin:
            obj = self.__builtin_expanders
        if statement in obj:
            raise KeyError("expander %s already provided" % (statement,))
        obj[SpecPreprocessor.PREFIX + statement] = \
            expander_callback

    def _add_builtin_expanders(self):
        # import statement
        self._add_expander("import", self._import_expander, builtin = True)

    def _import_expander(self, line):

        rest_line = line.split(" ", 1)[1].strip()
        if not rest_line:
            return line

        if rest_line.startswith(os.path.sep):
            # absolute path
            path = rest_line
        else:
            path = os.path.join(os.path.dirname(self._spec_path),
                rest_line)
        if not (os.path.isfile(path) and os.access(path, os.R_OK)):
            raise SpecPreprocessor.PreprocessorError(
                "invalid preprocessor line: %s" % (line,))

        with open(path, "r") as spec_f:
            lines = ''
            for line in spec_f.readlines():
                # call recursively
                split_line = line.split(" ", 1)
                if split_line:
                    expander = self.__builtin_expanders.get(split_line[0])
                    if expander is not None:
                        line = expander(line)
                lines += line

        return lines

    def parse(self):

        content = []
        with open(self._spec_path, "r") as spec_f:
            for line in spec_f.readlines():
                split_line = line.split(" ", 1)
                if split_line:
                    expander = self.__builtin_expanders.get(split_line[0])
                    if expander is not None:
                        line = expander(line)
                content.append(line)

        final_content = []
        for line in content:
            split_line = line.split(" ", 1)
            if split_line:
                expander = self.__expanders.get(split_line[0])
                if expander is not None:
                    line = expander(line)
            final_content.append(line)

        final_content = (''.join(final_content)).split("\n")

        return final_content


class SpecParser:

    def __init__(self, filepath):

        self.filepath = filepath[:]
        self._preprocessor = SpecPreprocessor(self.filepath)

        # FIXME: kept for backward .spec files compatibility where
        # execution_strategy argument is not set
        # TODO: remove and make execution_strategy mandatory in .spec file
        from molecule.specs.plugins.builtin_plugin import LivecdSpec

        execution_strategy = self.parse_execution_strategy()
        if execution_strategy is None:
            execution_strategy = LivecdSpec.execution_strategy()

        from molecule.specs.factory import PluginFactory
        spec_plugins = PluginFactory.get_spec_plugins()

        plugin = spec_plugins.get(execution_strategy)
        if plugin is None:
            raise SpecFileError("Execution strategy provided in %s spec file"
                " not supported, strategy: %s" % (
                    self.filepath, execution_strategy,))

        self.__plugin = plugin()
        self.vital_parameters = self.__plugin.vital_parameters()
        self.parser_data_path = self.__plugin.parser_data_path()


    def parse_execution_strategy(self):
        data = self._generic_parser()
        exc_str = GenericSpec.EXECUTION_STRATEGY_KEY
        for line in data:
            if not line.startswith(exc_str):
                continue
            key, value = self.parse_line_statement(line)
            if key is None:
                continue
            if key != exc_str:
                # wtf?
                continue
            return value

    def parse_line_statement(self, line_stmt):
        try:
            key, value = line_stmt.split(":", 1)
        except ValueError:
            return None, None
        key, value = key.strip(), value.strip()
        return key, value

    def parse(self):
        mydict = {}
        data = self._generic_parser()
        # compact lines properly
        old_key = None
        for line in data:
            key = None
            value = None
            v_key, v_value = self.parse_line_statement(line)
            check_dict = self.parser_data_path.get(v_key)
            if check_dict is not None:
                key, value = v_key, v_value
                old_key = key
            elif isinstance(old_key, get_stringtype()):
                key = old_key
                value = line.strip()
                if not value:
                    continue
            # gather again... key is changed
            check_dict = self.parser_data_path.get(key)
            if not isinstance(check_dict, dict):
                continue
            value = check_dict['ve'](value)
            if not check_dict['cb'](value):
                continue
            if key in mydict:
                if isinstance(value, get_stringtype()):
                    mydict[key] += " %s" % (value,)
                elif isinstance(value, list):
                    mydict[key] += value
                else:
                    continue
            else:
                mydict[key] = value
        mydict['__plugin__'] = self.__plugin
        self.validate_parse(mydict)
        return mydict.copy()

    def validate_parse(self, mydata):
        for param in self.vital_parameters:
            if param not in mydata:
                raise SpecFileError(
                    "SpecFileError: '%s' missing or invalid"
                    " '%s' parameter, it's vital. Your specification"
                    " file is incomplete!" % (self.filepath, param,)
                )

    def _generic_parser(self):
        data = []
        content = self._preprocessor.parse()
        # filter comments and white lines
        content = [x.strip().rsplit("#", 1)[0].strip() for x in content if \
            not x.startswith("#") and x.strip()]
        for line in content:
            if line in data:
                continue
            data.append(line)
        return data
