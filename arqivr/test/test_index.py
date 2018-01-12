#!/bin/env python
#
# Unit tests for the arqivr index module
import unittest
import os
import tempfile
import shutil
import time
from arqivr.index import FilesystemObjectType
from arqivr.index import FilesystemObject
from arqivr.index import ObjectIndex

#
# Tests
class TestFilesystemObject(unittest.TestCase):
    def setUp(self):
        # Create a temp working dir
        self.wd = tempfile.mkdtemp(suffix='TestFilesystemObject')
        self.pwd = os.getcwd()
        os.chdir(self.wd)

    def tearDown(self):
        os.chdir(self.pwd)
        for root,dirs,files in os.walk(self.wd):
            for name in dirs:
                os.chmod(os.path.join(root,name),0755)
            for name in files:
                try:
                    os.chmod(os.path.join(root,name),0644)
                except OSError:
                    pass
        shutil.rmtree(self.wd)

    def test_path(self):
        rel_path = "test"
        abs_path = os.path.abspath(rel_path)
        # Supply relative path
        self.assertEqual(FilesystemObject(rel_path).path,
                         abs_path)
        # Supply absolute path
        self.assertEqual(FilesystemObject(rel_path).path,
                         abs_path)

    def test_exists(self):
        # Doesn't exist
        self.assertFalse(FilesystemObject("test").exists)
        # File that exists
        with open("test.txt","w") as fp:
            fp.write("test")
        self.assertTrue(FilesystemObject("test.txt").exists)
        # Directory
        os.mkdir("test.dir")
        self.assertTrue(FilesystemObject("test.dir").exists)
        # Symlink
        os.symlink("test.txt","test.lnk")
        self.assertTrue(FilesystemObject("test.lnk").exists)
        # Broken symlink
        os.symlink("missing","missing.lnk")
        self.assertTrue(FilesystemObject("missing.lnk").exists)

    def test_timestamp(self):
        # Get current time in seconds
        timestamp = int(time.time())
        # Make file with known timestamp
        with open("test.txt","w") as fp:
            fp.write("test")
        os.utime("test.txt",(timestamp,timestamp))
        self.assertEqual(FilesystemObject("test.txt").timestamp,
                         timestamp)

    def test_size(self):
        # Make file
        with open("test.txt","w") as fp:
            fp.write("test")
        self.assertEqual(FilesystemObject("test.txt").size,4)

    def test_uid(self):
        # Get UID for current user
        current_uid = os.getuid()
        # Make file
        with open("test.txt","w") as fp:
            fp.write("test")
        self.assertEqual(FilesystemObject("test.txt").uid,
                         current_uid)

    def test_gid(self):
        # Get GID for current user
        current_gid = os.getgid()
        # Make file
        with open("test.txt","w") as fp:
            fp.write("test")
        self.assertEqual(FilesystemObject("test.txt").gid,
                         current_gid)

    def test_islink(self):
        # Doesn't exist
        self.assertFalse(FilesystemObject("test").islink)
        # File that exists
        with open("test.txt","w") as fp:
            fp.write("test")
        self.assertFalse(FilesystemObject("test.txt").islink)
        # Directory
        os.mkdir("test.dir")
        self.assertFalse(FilesystemObject("test.dir").islink)
        # Symlink
        os.symlink("test.txt","test.lnk")
        self.assertTrue(FilesystemObject("test.lnk").islink)
        # Broken symlink
        os.symlink("missing","missing.lnk")
        self.assertTrue(FilesystemObject("missing.lnk").islink)

    def test_isfile(self):
        # Doesn't exist
        self.assertFalse(FilesystemObject("test").isfile)
        # File that exists
        with open("test.txt","w") as fp:
            fp.write("test")
        self.assertTrue(FilesystemObject("test.txt").isfile)
        # Directory
        os.mkdir("test.dir")
        self.assertFalse(FilesystemObject("test.dir").isfile)
        # Symlink
        os.symlink("test.txt","test.lnk")
        self.assertFalse(FilesystemObject("test.lnk").isfile)
        # Broken symlink
        os.symlink("missing","missing.lnk")
        self.assertFalse(FilesystemObject("missing.lnk").isfile)

    def test_isdir(self):
        # Doesn't exist
        self.assertFalse(FilesystemObject("test").isdir)
        # File that exists
        with open("test.txt","w") as fp:
            fp.write("test")
        self.assertFalse(FilesystemObject("test.txt").isdir)
        # Directory
        os.mkdir("test.dir")
        self.assertTrue(FilesystemObject("test.dir").isdir)
        # Symlink
        os.symlink("test.txt","test.lnk")
        self.assertFalse(FilesystemObject("test.lnk").isdir)
        # Broken symlink
        os.symlink("missing","missing.lnk")
        self.assertFalse(FilesystemObject("missing.lnk").isdir)

    def test_type(self):
        # Doesn't exist
        self.assertEqual(FilesystemObject("test").type,
                         FilesystemObjectType.MISSING)
        # File that exists
        with open("test.txt","w") as fp:
            fp.write("test")
        self.assertEqual(FilesystemObject("test.txt").type,
                         FilesystemObjectType.FILE)
        # Directory
        os.mkdir("test.dir")
        self.assertEqual(FilesystemObject("test.dir").type,
                         FilesystemObjectType.DIRECTORY)
        # Symlink
        os.symlink("test.txt","test.lnk")
        self.assertEqual(FilesystemObject("test.lnk").type,
                         FilesystemObjectType.SYMLINK)
        # Broken symlink
        os.symlink("missing","missing.lnk")
        self.assertEqual(FilesystemObject("missing.lnk").type,
                         FilesystemObjectType.SYMLINK)

    def test_raw_symlink_target(self):
        # Make file and symlink
        with open("test.txt","w") as fp:
            fp.write("test")
        os.symlink("test.txt","test.lnk")
        self.assertEqual(
            FilesystemObject("test.lnk").raw_symlink_target,
            "test.txt")
        # Broken symlink
        os.symlink("missing","missing.lnk")
        self.assertEqual(
            FilesystemObject("missing.lnk").raw_symlink_target,
            "missing")

    def test_isaccessible(self):
        # Make test filesystem objects
        with open("test.txt","w") as fp:
            fp.write("test")
        self.assertTrue(FilesystemObject("test.txt").isaccessible)
        # Directory
        os.mkdir("test.dir")
        self.assertTrue(FilesystemObject("test.dir").isaccessible)
        # Symlink
        os.symlink("test.txt","test.lnk")
        self.assertTrue(FilesystemObject("test.lnk").isaccessible)
        # Broken symlink
        os.symlink("missing","missing.lnk")
        self.assertTrue(FilesystemObject("missing.lnk").isaccessible)
        # Set permissions to make objects unreadable
        os.chmod("test.txt",0044)
        self.assertFalse(FilesystemObject("test.txt").isaccessible)
        self.assertTrue(FilesystemObject("test.lnk").isaccessible)
        os.chmod("test.dir",0055)
        self.assertFalse(FilesystemObject("test.dir").isaccessible)

class TestObjectIndex(unittest.TestCase):
    def setUp(self):
        # Create a temp working dir
        self.wd = tempfile.mkdtemp(suffix='TestObjectIndex')
        self.pwd = os.getcwd()
        os.chdir(self.wd)

    def tearDown(self):
        os.chdir(self.pwd)
        for root,dirs,files in os.walk(self.wd):
            for name in dirs:
                os.chmod(os.path.join(root,name),0755)
            for name in files:
                try:
                    os.chmod(os.path.join(root,name),0644)
                except OSError:
                    pass
        shutil.rmtree(self.wd)

    def test_empty_objectindex(self):
        indx = ObjectIndex(self.wd)
        self.assertEqual(indx.names,[])
        self.assertEqual(len(indx),0)

    def test_populated_objectindex(self):
        # Add some objects to current dir
        dirs = ("test1.dir",
                "test2.dir",
                "test1.dir/sub.dir",)
        files = ("test.txt",
                 "test1.dir/test.txt",
                 "test2.dir/test.txt",)
        symlinks = { "test.lnk": "test.txt",
                     "test1.dir/sub.dir/test.lnk": "../test.txt" }
        for d in dirs:
            os.mkdir(d)
        for f in files:
            with open(f,"w") as fp:
                fp.write("test\n")
        for s in symlinks:
            os.symlink(symlinks[s],s)
        # Build the index
        indx = ObjectIndex(self.wd)
        indx.build()
        self.assertEqual(len(indx),8)
        # Check __contains__
        for d in dirs:
            self.assertTrue(d in indx)
        for d in files:
            self.assertTrue(f in indx)
        for s in symlinks:
            self.assertTrue(s in indx)
        self.assertFalse("missing" in indx)
        # Check names
        for n in indx.names:
            self.assertTrue((n in dirs) or
                            (n in files) or
                            (n in symlinks))
        # Check __getitem__
        for n in indx.names:
            obj = indx[n]
            self.assertTrue(isinstance(obj,
                                       FilesystemObject))
            self.assertEqual(obj.path,
                             os.path.join(self.wd,n))
