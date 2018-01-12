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
from arqivr.index import FilesystemObjectIndex
from arqivr.index import compare
from arqivr.index import check_accessibility

#
# Helper functions
def _remove_dir(dirn):
    for root,dirs,files in os.walk(dirn):
        for name in dirs:
            os.chmod(os.path.join(root,name),0755)
        for name in files:
            try:
                os.chmod(os.path.join(root,name),0644)
            except OSError:
                pass
    shutil.rmtree(dirn)
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
        _remove_dir(self.wd)

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

class TestFilesystemObjectIndex(unittest.TestCase):
    def setUp(self):
        # Create a temp working dir
        self.wd = tempfile.mkdtemp(suffix='TestObjectIndex')
        self.pwd = os.getcwd()
        os.chdir(self.wd)

    def tearDown(self):
        os.chdir(self.pwd)
        _remove_dir(self.wd)

    def test_empty_objectindex(self):
        indx = FilesystemObjectIndex(self.wd)
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
        indx = FilesystemObjectIndex(self.wd)
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
        # Don't like this way of invoking __getitem__
        # but seems to work for testing
        self.assertRaises(KeyError,indx.__getitem__,"missing")

class TestCompareFunction(unittest.TestCase):
    def setUp(self):
        # Create a temp working dir
        self.wd = tempfile.mkdtemp(suffix='TestCompareFunction')
        self.pwd = os.getcwd()
        os.chdir(self.wd)

    def tearDown(self):
        os.chdir(self.pwd)
        _remove_dir(self.wd)

    def _populate_dir(self,dirn):
        # Add some objects to current dir
        dirs = ("test1.dir",
                "test2.dir",
                "test3.dir",
                "test1.dir/sub.dir",)
        files = ("test.txt",
                 "test1.dir/test.txt",
                 "test2.dir/test.txt",)
        symlinks = { "test.lnk": "test.txt",
                     "test1.dir/sub.dir/test.lnk": "../test.txt",
                     "test1.lnk": "test1.dir",
                     "test2.lnk": "test2.dir" }
        for d in dirs:
            os.mkdir(os.path.join(dirn,d))
        for f in files:
            with open(os.path.join(dirn,f),"w") as fp:
                fp.write("blah\n")
        for s in symlinks:
            os.symlink(symlinks[s],os.path.join(dirn,s))
        return (dirs,files,symlinks)

    def _copy_dir(self,src,tgt):
        # Copy directory tree and attributes
        #shutil.copytree(src,tgt,symlinks=True)
        #Would prefer to use shutil.copytree but this doesn't
        #seem to preserve timestamps
        os.system("cp -aR %s %s" % (src,tgt))

    def test_compare_empty(self):
        os.mkdir("test1")
        indx1 = FilesystemObjectIndex("test1")
        indx1.build()
        os.mkdir("test2")
        indx2 = FilesystemObjectIndex("test2")
        indx2.build()
        diff = compare(indx1,indx2)
        self.assertEqual(diff.missing,[])
        self.assertEqual(diff.extra,[])
        self.assertEqual(diff.restricted_source,[])
        self.assertEqual(diff.restricted_target,[])
        self.assertEqual(diff.changed_type,[])
        self.assertEqual(diff.changed_size,[])
        self.assertEqual(diff.changed_link,[])
        self.assertEqual(diff.changed_time,[])

    def test_compare_no_differences(self):
        os.mkdir("test1")
        self._populate_dir("test1")
        self._copy_dir("test1","test2")
        indx1 = FilesystemObjectIndex("test1")
        indx1.build()
        indx2 = FilesystemObjectIndex("test2")
        indx2.build()
        diff = compare(indx1,indx2)
        self.assertEqual(diff.missing,[])
        self.assertEqual(diff.extra,[])
        self.assertEqual(diff.restricted_source,[])
        self.assertEqual(diff.restricted_target,[])
        self.assertEqual(diff.changed_type,[])
        self.assertEqual(diff.changed_size,[])
        self.assertEqual(diff.changed_link,[])
        self.assertEqual(diff.changed_time,[])

    def test_compare_with_differences(self):
        # Make reference directory
        os.mkdir("test1")
        self._populate_dir("test1")
        # Make directory to compare
        self._copy_dir("test1","test2")
        # Remove a file (missing)
        os.remove("test2/test.txt")
        # Add a new file (extra)
        with open("test2/test2.dir/new.txt","w") as fp:
            fp.write("blah")
        # Change content (changed_size)
        with open("test2/test2.dir/test.txt","w") as fp:
            fp.write("blah")
        # Build indexes
        indx1 = FilesystemObjectIndex("test1")
        indx2 = FilesystemObjectIndex("test2")
        indx1.build()
        indx2.build()
        # Do comparison
        diff = compare(indx1,indx2)
        self.assertEqual(diff.missing,["test.txt"])
        self.assertEqual(diff.extra,["test2.dir/new.txt"])
        self.assertEqual(diff.restricted_source,[])
        self.assertEqual(diff.restricted_target,[])
        self.assertEqual(diff.changed_type,[])
        self.assertEqual(diff.changed_size,["test2.dir/test.txt"])
        self.assertEqual(diff.changed_link,[])
        self.assertEqual(diff.changed_time,["test2.dir",
                                            "test2.dir/test.txt"])

    def test_compare_with_changed_types(self):
        # Make reference directory
        os.mkdir("test1")
        self._populate_dir("test1")
        # Make directory to compare
        self._copy_dir("test1","test2")
        # Change a file to a directory
        os.remove("test2/test.txt")
        os.mkdir("test2/test.txt")
        # Change a file to a link
        os.remove("test2/test2.dir/test.txt")
        os.symlink(".","test2/test2.dir/test.txt")
        # Change a directory to a file
        shutil.rmtree("test2/test1.dir")
        with open("test2/test1.dir","w") as fp:
            fp.write("blah")
        # Change a directory to a link
        shutil.rmtree("test2/test3.dir")
        os.symlink(".","test2/test3.dir")
        # Change a link to a file
        os.remove("test2/test1.lnk")
        with open("test2/test1.lnk","w") as fp:
            fp.write("blah")
        # Change a link to a directory
        os.remove("test2/test2.lnk")
        os.mkdir("test2/test2.lnk")
        # Build indexes
        indx1 = FilesystemObjectIndex("test1")
        indx2 = FilesystemObjectIndex("test2")
        indx1.build()
        indx2.build()
        # Do comparison
        diff = compare(indx1,indx2)
        self.assertEqual(diff.missing,["test1.dir/sub.dir",
                                       "test1.dir/sub.dir/test.lnk",
                                       "test1.dir/test.txt"])
        self.assertEqual(diff.extra,[])
        self.assertEqual(diff.restricted_source,[])
        self.assertEqual(diff.restricted_target,[])
        self.assertEqual(diff.changed_type,["test.txt",
                                            "test1.dir",
                                            "test1.lnk",
                                            "test2.dir/test.txt",
                                            "test2.lnk",
                                            "test3.dir"])
        self.assertEqual(diff.changed_size,[])
        self.assertEqual(diff.changed_link,[])
        self.assertEqual(diff.changed_time,["test2.dir"])

    def test_compare_with_changed_symlink(self):
        # Make reference directory
        os.mkdir("test1")
        self._populate_dir("test1")
        # Make directory to compare
        self._copy_dir("test1","test2")
        # Change link target (changed_link)
        os.remove("test2/test.lnk")
        os.symlink("test1.dir","test2/test.lnk")
        # Build indexes
        indx1 = FilesystemObjectIndex("test1")
        indx2 = FilesystemObjectIndex("test2")
        indx1.build()
        indx2.build()
        # Do comparison
        diff = compare(indx1,indx2)
        self.assertEqual(diff.missing,[])
        self.assertEqual(diff.extra,[])
        self.assertEqual(diff.restricted_source,[])
        self.assertEqual(diff.restricted_target,[])
        self.assertEqual(diff.changed_type,[])
        self.assertEqual(diff.changed_size,[])
        self.assertEqual(diff.changed_link,["test.lnk"])
        self.assertEqual(diff.changed_time,["test.lnk"])

    def test_compare_with_restricted_objects(self):
        # Make reference directory
        os.mkdir("test1")
        self._populate_dir("test1")
        # Make directory to compare
        self._copy_dir("test1","test2")
        # Remove permissions on source subdir (restricted_source)
        os.chmod("test1/test1.dir",0055)
        # Remove permissions on target subdir (restricted_target)
        os.chmod("test2/test2.dir",0055)
        # Build indexes
        indx1 = FilesystemObjectIndex("test1")
        indx2 = FilesystemObjectIndex("test2")
        indx1.build()
        indx2.build()
        # Do comparison
        diff = compare(indx1,indx2)
        self.assertEqual(diff.missing,["test2.dir/test.txt"])
        self.assertEqual(diff.extra,["test1.dir/sub.dir",
                                     "test1.dir/sub.dir/test.lnk",
                                     "test1.dir/test.txt"])
        self.assertEqual(diff.restricted_source,["test1.dir"])
        self.assertEqual(diff.restricted_target,["test2.dir"])
        self.assertEqual(diff.changed_type,[])
        self.assertEqual(diff.changed_size,[])
        self.assertEqual(diff.changed_link,[])
        self.assertEqual(diff.changed_time,[])

class TestCheckAccessibilityFunction(unittest.TestCase):
    def setUp(self):
        # Create a temp working dir
        self.wd = tempfile.mkdtemp(suffix='TestAccessibilityFunction')
        self.pwd = os.getcwd()
        os.chdir(self.wd)

    def tearDown(self):
        os.chdir(self.pwd)
        _remove_dir(self.wd)

    def _populate_dir(self,dirn):
        # Add some objects to current dir
        dirs = ("test1.dir",
                "test2.dir",
                "test3.dir",
                "test1.dir/sub.dir",)
        files = ("test.txt",
                 "test1.dir/test.txt",
                 "test2.dir/test.txt",)
        symlinks = { "test.lnk": "test.txt",
                     "test1.dir/sub.dir/test.lnk": "../test.txt",
                     "test1.lnk": "test1.dir",
                     "test2.lnk": "test2.dir" }
        for d in dirs:
            os.mkdir(os.path.join(dirn,d))
        for f in files:
            with open(os.path.join(dirn,f),"w") as fp:
                fp.write("blah\n")
        for s in symlinks:
            os.symlink(symlinks[s],os.path.join(dirn,s))
        return (dirs,files,symlinks)

    def test_check_accessibility_without_restricted_objects(self):
        # Make reference directory
        os.mkdir("test")
        self._populate_dir("test")
        # Build index
        indx = FilesystemObjectIndex("test")
        indx.build()
        self.assertEqual(check_accessibility(indx),[])

    def test_check_accessibility_with_restricted_objects(self):
        # Make reference directory
        os.mkdir("test")
        self._populate_dir("test")
        # Remove permissions on subdir
        os.chmod("test/test1.dir",0055)
        # Remove permissions on file
        os.chmod("test/test2.dir/test.txt",0044)
        # Build index
        indx = FilesystemObjectIndex("test")
        indx.build()
        self.assertEqual(check_accessibility(indx),
                         ["test1.dir",
                          "test2.dir/test.txt"])
