#!/bin/env python
#
#     index.py: indexing classes and functions
#     Copyright (C) University of Manchester 2018 Peter Briggs
#

"""
Indexing classes and functions
"""

import os
import stat
import collections

# File types
class FilesystemObjectType(object):
    FILE = 0
    DIRECTORY = 1
    SYMLINK = 2
    UNKNOWN = 3

class FilesystemObject(object):
    """
    Store information about file system object
    """
    def __init__(self,path):
        """
        """
        self.path = path
        try:
            self._st = os.lstat(self.path)
        except OSError:
            self._st = None

    @property
    def exists(self):
        return os.path.lexists(self.path)

    @property
    def timestamp(self):
        return self._st.st_mtime

    @property
    def size(self):
        return self._st.st_size

    @property
    def uid(self):
        return self._st.st_uid

    @property
    def gid(self):
        return self._st.st_gid
    
    @property
    def islink(self):
        return os.path.islink(self.path)

    @property
    def isfile(self):
        if not self.islink:
            return os.path.isfile(self.path)
        return False

    @property
    def isdir(self):
        if not self.islink:
            return os.path.isdir(self.path)
        return False

    @property
    def type(self):
        if self.isfile:
            return FilesystemObjectType.FILE
        elif self.isdir:
            return FilesystemObjectType.DIRECTORY
        elif self.islink:
            return FilesystemObjectType.SYMLINK
        else:
            return FilesystemObjectType.UNKNOWN

    @property
    def raw_symlink_target(self):
        return os.readlink(self.path)

    @property
    def isaccessible(self):
        st_mode = self._st.st_mode
        if self.uid == os.getuid():
            return bool(st_mode & stat.S_IRUSR)
        if self.gid in os.getgroups():
            return bool(st_mode & stat.S_IRGRP)
        return bool(st_mode & stat.S_IROTH)

class ObjectIndex(object):
    """
    Index of information about objects in a directory
    """
    def __init__(self,dirn):
        """
        """
        self._dirn = os.path.abspath(dirn)
        self._objects = {}
        self._names = []

    def __len__(self):
        return len(self._objects)

    def __contains__(self,name):
        return (name in self._names)

    def __getitem__(self,name):
        return self._objects[name]

    @property
    def names(self):
        """
        Return list of object names
        """
        return [x for x in self._names]
    
    def build(self):
        """
        Build index from filesystem
        """
        print "Indexing objects in %s" % self._dirn
        for d in os.walk(self._dirn):
            for f in d[1]:
                self._add_object(d[0],f)
            for f in d[2]:
                self._add_object(d[0],f)
        print "Added %d objects" % len(self)
        return self

    def _add_object(self,*args):
        """
        Store info about a filesystem object
        """
        # Get absolute and relative paths
        path = os.path.normpath(os.path.join(*args))
        relpath = os.path.relpath(path,self._dirn)
        # Store the object
        self._objects[relpath] = FilesystemObject(path)
        self._names.append(relpath) # Use a set instead?

def compare(src,tgt):
    """
    Compare two ObjectIndexes
    """
    # Define a named tuple to return the results with
    ObjectIndexComparison = collections.namedtuple(
    "ObjectIndexComparison",
    ['missing',
     'extra',
     'restricted_source',
     'restricted_target',
     'changed_type',
     'changed_size',
     'changed_link',
     'changed_time',],)
    # Missing and modified objects
    missing = set()
    changed_type = set()
    changed_size = set()
    changed_link = set()
    changed_time = set()
    restricted_src = set()
    restricted_tgt = set()
    for name in src.names:
        src_obj = src[name]
        if not src_obj.isaccessible:
            restricted_src.add(name)
        if name not in tgt:
            missing.add(name)
        else:
            tgt_obj = tgt[name]
            if not tgt_obj.isaccessible:
                restricted_tgt.add(name)
            elif src_obj.type != tgt_obj.type:
                changed_type.add(name)
            else:
                if src_obj.type == FilesystemObjectType.FILE:
                    if src_obj.size != tgt_obj.size:
                        changed_size.add(name)
                elif src_obj.type == FilesystemObjectType.SYMLINK:
                    if src_obj.raw_symlink_target != tgt_obj.raw_symlink_target:
                        changed_link.add(name)
                if src_obj.timestamp != tgt_obj.timestamp:
                    changed_time.add(name)
    # Extra objects
    extra = set()
    for name in tgt.names:
        if name not in src:
            extra.add(name)
        tgt_obj = tgt[name]
        if not tgt_obj.isaccessible:
            restricted_tgt.add(name)
    # Return the results
    return ObjectIndexComparison(
        missing=sorted(list(missing)),
        extra=sorted(list(extra)),
        restricted_source=sorted(list(restricted_src)),
        restricted_target=sorted(list(restricted_tgt)),
        changed_type=sorted(list(changed_type)),
        changed_size=sorted(list(changed_size)),
        changed_link=sorted(list(changed_link)),
        changed_time=sorted(list(changed_time)))
            
def check_accessibility(indx):
    """
    Check objects in an ObjectIndex are accessible
    """
    inaccessible = []
    for name in indx.names:
        obj = indx[name]
        if not obj.isaccessible:
            inaccessible.append(name)
    return inaccessible
