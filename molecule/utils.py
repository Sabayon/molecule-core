#!/usr/bin/python -O
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
import sys
import time
import subprocess
import shutil

RUNNING_PIDS = set()

def get_year():
    return time.strftime("%Y")

def valid_exec_check(path):
    with open("/dev/null","w") as f:
        p = subprocess.Popen([path], stdout = f, stderr = f)
        rc = p.wait()
        if rc == 127:
            raise EnvironmentError("EnvironmentError: %s not found" % (path,))

def is_exec_available(exec_name):
    paths = os.getenv("PATH")
    if not paths: return False
    paths = paths.split(":")
    for path in paths:
        path = os.path.join(path,exec_name)
        if os.path.isfile(path) and os.access(path,os.X_OK):
            return True
    return False

def exec_cmd(args):
    # do not use Popen otherwise it will try to replace
    # wildcards automatically ==> rsync no workie
    return subprocess.call(' '.join(args), shell = True)

def exec_chroot_cmd(args, chroot, pre_chroot = []):
    pid = os.fork()
    if pid == 0:
        os.chroot(chroot)
        os.chdir("/")
        myargs = pre_chroot+args
        rc = subprocess.call(myargs)
        os._exit(rc)
    else:
        RUNNING_PIDS.add(pid)
        rcpid, rc = os.waitpid(pid,0)
        RUNNING_PIDS.discard(pid)
        return rc

def empty_dir(dest_dir):
    for el in os.listdir(dest_dir):
        el = os.path.join(dest_dir,el)
        if os.path.isfile(el) or os.path.islink(el):
            os.remove(el)
        elif os.path.isdir(el):
            shutil.rmtree(el,True)
            if os.path.isdir(el):
                os.rmdir(el)

# using subprocess.call to not care about wildcards
def remove_path(path):
    return subprocess.call('rm -rf %s' % (path,), shell = True)

def remove_path_sandbox(path, sandbox_env):
    p = subprocess.Popen(' '.join(["sandbox", "rm", "-rf", path]),
        stdout = sys.stdout, stderr = sys.stderr,
        env = sandbox_env, shell = True
    )
    return p.wait()

def get_random_number():
    return abs(hash(os.urandom(2)))%99999

def md5sum(filepath):
    import hashlib
    m = hashlib.md5()
    readfile = open(filepath)
    block = readfile.read(1024)
    while block:
        m.update(block)
        block = readfile.read(1024)
    readfile.close()
    return m.hexdigest()

def copy_dir(src_dir, dest_dir):
    args = ["cp", "-Rap", src_dir, dest_dir]
    return exec_cmd(args)

def print_traceback(f = None):
    """
    Function called when an exception occurs with the aim to give
    user a clue of what went wrong.

    @keyword f: write to f (file) object instead of stdout
    @type f: valid file handle
    """
    import traceback
    traceback.print_exc(file = f)