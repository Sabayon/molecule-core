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
from molecule.exception import SpecFileError
from molecule.specs.plugins import SPEC_PLUGS
from molecule.specs.plugins.builtin import LivecdSpec
from molecule.specs.skel import GenericSpec
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
            'version': "0.5.4",
            'chroot_compressor': "mksquashfs",
            'iso_builder': "mkisofs",
            'mirror_syncer': "rsync",
            'chroot_compressor_builtin_args': ["-noappend", "-no-progress"],
            'iso_builder_builtin_args': ["-J", "-R", "-l", "-no-emul-boot",
                "-boot-load-size", "4", "-udf", "-boot-info-table"],
            'mirror_syncer_builtin_args': ["-a", "--delete", "--delete-excluded",
                "--delete-during", "--numeric-ids", "--recursive", "-d", "-A", "-H"],
            'chroot_compressor_output_file': "livecd.squashfs",
            'iso_mounter': ["mount", "-o", "loop", "-t", "iso9660"],
            'iso_umounter': ["umount"],
            'squash_mounter': ["mount", "-o", "loop", "-t", "squashfs"],
            'squash_umounter': ["umount"],
            'pkgs_adder': ["equo", "install"],
            'pkgs_remover': ["equo", "remove"],
            'pkgs_updater': ["equo", "update"],
        }
        self.clear()
        self.update(settings)
        self.update(mysettings)

        paths_to_check = ["chroot_compressor", "iso_builder", "mirror_syncer"]
        for key in paths_to_check:
            molecule.utils.valid_exec_check(self.get(key))



class SpecParser:

    # FIXME: kept for backward .spec files compatibility where
    # execution_strategy argument is not set
    DEFAULT_PARSER = LivecdSpec

    def __init__(self, filepath):

        self.filepath = filepath[:]
        execution_strategy = self.parse_execution_strategy()
        if execution_strategy is None:
            execution_strategy = SpecParser.DEFAULT_PARSER.execution_strategy()

        plugin = SPEC_PLUGS.get(execution_strategy)
        if plugin is None:
            raise SpecFileError("Execution strategy provided in %s spec file"
                " not supported, strategy: %s" % (
                    self.filepath, execution_strategy,))

        self.__plugin = plugin()
        self.vital_parameters = self.__plugin.vital_parameters()
        self.parser_data_path = self.__plugin.parser_data_path()


    def parse_execution_strategy(self):
        data = self.__generic_parser(self.filepath)
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
        data = self.__generic_parser(self.filepath)
        # compact lines properly
        old_key = None
        for line in data:
            if ":" in line:
                key, value = self.parse_line_statement(line)
                if key is None:
                    continue
                old_key = key
            elif isinstance(old_key, basestring):
                key = old_key
                value = line.strip()
                if not value:
                    continue
            check_dict = self.parser_data_path.get(key)
            if not isinstance(check_dict, dict):
                continue
            value = check_dict['ve'](value)
            if not check_dict['cb'](value):
                continue
            if key in mydict:
                if isinstance(value, basestring):
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
                    " file is incomplete!" % (self.filepath,param,)
                )

    def __generic_parser(self, filepath):
        with open(filepath,"r") as f:
            data = []
            content = f.readlines()
            f.close()
            # filter comments and white lines
            content = [x.strip().rsplit("#", 1)[0].strip() for x in content if \
                not x.startswith("#") and x.strip()]
            for line in content:
                if line in data:
                    continue
                data.append(line)
            return data
