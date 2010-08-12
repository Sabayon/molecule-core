# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0,'.')
sys.path.insert(0,'..')
import unittest
import tempfile
from molecule.compat import get_stringtype
from molecule.utils import md5sum, copy_dir, get_random_number, \
    remove_path_sandbox, remove_path, mkdtemp, empty_dir, \
    exec_cmd_get_status_output, exec_cmd, is_exec_available, \
    valid_exec_check, get_year, exec_chroot_cmd

class UtilsTest(unittest.TestCase):

    def setUp(self):
        sys.stdout.write("%s called\n" % (self,))
        sys.stdout.flush()

    def tearDown(self):
        """
        tearDown is run after each test
        """
        sys.stdout.write("%s ran\n" % (self,))
        sys.stdout.flush()

    def test_md5sum(self):

        tmp_fd, tmp_path = tempfile.mkstemp(dir=os.getcwd())
        os.write(tmp_fd, "hello")
        os.close(tmp_fd)
        result = md5sum(tmp_path)
        self.assertEqual(result, "5d41402abc4b2a76b9719d911017c592")
        os.remove(tmp_path)

    def test_copy_dir(self):
        tmp_dir1 = tempfile.mkdtemp(dir=os.getcwd())
        tmp_dir2 = tempfile.mkdtemp(dir=os.getcwd())
        tmp_path1 = os.path.join(tmp_dir1, "test")
        tmp_path2 = os.path.join(tmp_dir2, "test")
        tmp_f = open(tmp_path1, "w")
        tmp_f.write("hello")
        tmp_f.close()
        os.rmdir(tmp_dir2)
        copy_dir(tmp_dir1, tmp_dir2)
        self.assertEqual(os.listdir(tmp_dir2), ['test'])
        os.remove(tmp_path1)
        os.rmdir(tmp_dir1)
        os.remove(tmp_path2)
        os.rmdir(tmp_dir2)

    def test_randint(self):
        self.assert_(get_random_number() in range(0, 99999))

    def test_sandbox_rm(self):
        tmp_dir1 = tempfile.mkdtemp(dir=os.getcwd())
        tmp_dir2 = tempfile.mkdtemp(dir=os.getcwd())
        sb_dirs = [tmp_dir1]
        sb_env = {
            'SANDBOX_WRITE': ':'.join(sb_dirs),
        }
        rc = remove_path_sandbox(tmp_dir1, sb_env)
        self.assert_(rc == 0)
        tmp_fd, tmp_path = tempfile.mkstemp()
        with os.fdopen(tmp_fd, "w") as tmp_f:
            rc = remove_path_sandbox(tmp_dir2, sb_env, stdout=tmp_fd,
                stderr=tmp_fd)
        os.remove(tmp_path)
        self.assert_(rc != 0)
        os.rmdir(tmp_dir2)

    def test_normal_rm(self):
        tmp_dir1 = tempfile.mkdtemp(dir=os.getcwd())
        tmp_fd, tmp_path = tempfile.mkstemp()
        os.close(tmp_fd)
        rc = remove_path(tmp_path)
        rc2 = remove_path(tmp_dir1)
        self.assert_(rc == 0)
        self.assert_(rc2 == 0)
        self.assert_(not os.path.lexists(tmp_path))
        self.assert_(not os.path.lexists(tmp_dir1))

    def test_mkdtemp(self):
        tmp_dir1 = mkdtemp()
        self.assert_(os.path.isdir(tmp_dir1))
        os.rmdir(tmp_dir1)

    def test_empty_dir(self):
        tmp_dir1 = tempfile.mkdtemp(dir=os.getcwd())
        tmp_f = open(os.path.join(tmp_dir1, "test"), "w")
        tmp_f.write("something")
        tmp_f.close()
        empty_dir(tmp_dir1)
        self.assert_(not os.listdir(tmp_dir1))
        os.rmdir(tmp_dir1)

    def test_exec_cmd_get_status_output(self):
        rc, output = exec_cmd_get_status_output(["echo", "hello"])
        self.assert_(rc == 0)
        self.assertEqual(output, "hello")

    def test_exec_cmd(self):
        rc = exec_cmd(["/bin/echo", "${TEST}"], env = {'TEST': "hello"})
        self.assert_(rc == 0)

    def test_is_exec_available(self):
        self.assert_(is_exec_available("/bin/echo"))

    def test_valid_exec_check(self):
        self.assertRaises(EnvironmentError,
            valid_exec_check, "/bin/this-does-not-exist-for-sure")

    def test_get_year(self):
        year = int(get_year())
        self.assert_(year in range(1970, 2138))

    def test_exec_chroot_cmd(self):
        rc = exec_chroot_cmd(["/bin/echo", "hello"], "/", env = {})
        self.assert_(rc == 0)

if __name__ == '__main__':
    unittest.main()
    raise SystemExit(0)
