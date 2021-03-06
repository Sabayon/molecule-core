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
import errno
import fcntl
import sys
import time
import tempfile
import subprocess
import signal
import shutil
import glob
import random
random.seed()

from molecule.compat import convert_to_rawstring


def get_year():
    """
    Return current year string.
    """
    return time.strftime("%Y")

def is_super_user():
    """
    Return True if current process has uid = 0.
    """
    return os.getuid() == 0

def valid_exec_check(path):
    """
    Determine whethern give path is valid executable (by running it).
    """
    tmp_fd, tmp_path = None, None
    try:
        tmp_fd, tmp_path = tempfile.mkstemp()
        p = subprocess.Popen([path], stdout = tmp_fd, stderr = tmp_fd)
        rc = p.wait()
        if rc == 127:
            raise EnvironmentError("EnvironmentError: %s not found" % (path,))
    except OSError as err:
        if err.errno != errno.ENOENT:
            raise
        raise EnvironmentError("EnvironmentError: %s not found" % (path,))
    finally:
        if tmp_fd is not None:
            os.close(tmp_fd)
        if tmp_path is not None:
            os.remove(tmp_path)

def is_exec_available(exec_name):
    """
    Determine whether given executable name is available in PATH.
    PATH must be set in environment.
    """
    paths = os.getenv("PATH")
    if not paths:
        return False
    paths = paths.split(":")
    for path in paths:
        path = os.path.join(path, exec_name)
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return True
    return False

def eval_shell_argument(argument, env = None):
    """
    Evaluate a single shell argument (taken from a full
    shlex.split()) replacing the environment variables with
    actual values and executing functions and external commands
    as well (so pay attention, command injection is actually a
    wanted side-effect).

    In case of errors, AttributeError() is raised.
    """
    read, write = None, None
    try:
        shell_exec = os.getenv("SHELL", "/bin/sh")
        read, write = os.pipe()
        # set non-blocking
        fcntl.fcntl(read, fcntl.F_SETFL, os.O_NONBLOCK)
        exit_st = subprocess.call(
            [shell_exec, "-c",
            "printf '%s' \"" + argument + "\""],
        env = env, stdout = write)
        if exit_st != 0:
            raise AttributeError(
                "error while parsing argument: '%s'" % (
                    argument,))
        # maximum 1024 chars
        try:
            evaluated = os.read(read, 1024)
        except OSError as err:
            # errno 11 is due to O_NONBLOCK
            if err.errno == errno.EAGAIN:
                raise AttributeError(
                    "error while parsing argument: '%s'" %(
                        argument,))
            raise
        return evaluated
    finally:
        if read is not None:
            try:
                os.close(read)
            except OSError:
                pass
        if write is not None:
            try:
                os.close(write)
            except OSError:
                pass

def exec_cmd(args, env = None):
    return subprocess.call(args, env = env)

def exec_cmd_get_status_output(args):
    """Return (status, output) of executing cmd in a shell."""
    pipe = os.popen('{ ' + ' '.join(args) + '; } 2>&1', 'r')
    text = pipe.read()
    sts = pipe.close()
    if sts is None:
        sts = 0
    if text[-1:] == '\n':
        text = text[:-1]
    return sts, text

def exec_chroot_cmd(args, chroot, pre_chroot = None, env = None):
    """
    Execute a command inside a chroot.
    """
    if pre_chroot is None:
        pre_chroot = []
    if env is None:
        env = os.environ.copy()
    exec_args = pre_chroot + [
        "chroot", chroot] + args
    return subprocess.call(exec_args, env=env)

def kill_chroot_pids(chroot, sig = signal.SIGTERM, sleep = False):
    """
    Kill stale processes inside chroot or directory
    """
    args = ["/usr/bin/lsof", "-t", chroot]
    if sleep:
        # give time to failing stuff to fail definitely and spawn all the
        # possible, processes. It is really hard to kill them all when there
        # is bash involved.
        time.sleep(5.0)
    sts, txt = exec_cmd_get_status_output(args)
    if sts == 0:
        killed_pids = []
        for pid_str in txt.strip().split():
            try:
                pid = int(pid_str)
            except (ValueError, TypeError):
                continue
            try:
                os.kill(pid, sig)
                killed_pids.append(pid)
            except (OSError, IOError):
                sts = 1
        if (sts == 0) and killed_pids:
            time.sleep(2.0)
            # are we done? nested call if not
            return kill_chroot_pids(chroot, sig = sig, sleep = False)
        return sts
    else:
        return sts

def empty_dir(dest_dir):
    """
    Remove the content of a directory in a safe way.
    """
    for el in os.listdir(dest_dir):
        el = os.path.join(dest_dir, el)
        if os.path.isfile(el) or os.path.islink(el):
            os.remove(el)
        elif os.path.isdir(el):
            shutil.rmtree(el, True)
            if os.path.isdir(el):
                os.rmdir(el)

def mkdtemp(suffix=''):
    """
    Generate a reliable temporary directory inside MOLECULE_TMPDIR
    env var (/var/tmp) starting with "molecule".
    """
    import molecule.settings
    tmp_dir = molecule.settings.Configuration()['tmp_dir']
    return tempfile.mkdtemp(prefix = "molecule", dir = tmp_dir,
        suffix = suffix)

# using subprocess.call to not care about wildcards
def remove_path(path):
    """
    Remove path, calling "rm -rf path".
    """
    return subprocess.call('rm -rf %s' % (path,), shell = True)

def remove_path_sandbox(path, sandbox_env, stdout = None, stderr = None):
    """
    Remove path, using a sandbox.
    """
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    p = subprocess.Popen(["sandbox", "rm", "-rf"] + glob.glob(path),
        stdout = stdout, stderr = stderr,
        env = sandbox_env
    )
    return p.wait()

def get_random_number():
    """
    Get a random number, it uses os.urandom()
    """
    return random.randint(0, 99999)

def get_random_str(str_len):
    """
    Return a random string of length str_len. It uses os.urandom()
    @param str_len: byte length
    @type str_len: int
    @return: random string
    @rtype: str
    """
    return os.urandom(str_len)

def md5sum(filepath):
    """
    Calcuate md5 hash of given file path.
    """
    import hashlib
    m = hashlib.md5()
    readfile = open(filepath, "rb")
    block = readfile.read(1024)
    while block:
        m.update(convert_to_rawstring(block))
        block = readfile.read(1024)
    readfile.close()
    return m.hexdigest()

def copy_dir(src_dir, dest_dir):
    """
    Copy a directory src (src_dir) to dst (dest_dir) using cp -Rap.
    """
    args = ["cp", "-Rap", src_dir, dest_dir]
    return exec_cmd(args)

def copy_dir_existing_dest(src_dir, dest_dir):
    """
    Copy a directory src (src_dir) to dst (dest_dir) using cp -Rap.
    This variant takes into consideration the fact that destination
    directory exists.
    """
    source_objects = []
    for obj in os.listdir(src_dir):
        source_objects.append(os.path.join(src_dir, obj))
    args = ["cp", "-Rap"] + source_objects + [dest_dir + "/"]
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
