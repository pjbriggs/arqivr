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
import hashlib
import pwd
import grp

# Constants
MD5_BLOCK_SIZE = 1024*1024

# File types
class FilesystemObjectType(object):
    FILE = 0
    DIRECTORY = 1
    SYMLINK = 2
    MISSING = 3
    UNKNOWN = 4

class FilesystemObject(object):
    """
    Store information about file system object
    """
    def __init__(self,path):
        """
        """
        self.path = os.path.abspath(path)
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
    def username(self):
        uid = self.uid
        try:
            return pwd.getpwuid(int(uid)).pw_name
        except (KeyError,ValueError,OverflowError):
            return uid

    @property
    def gid(self):
        return self._st.st_gid

    @property
    def groupname(self):
        gid = self.gid
        try:
            return grp.getgrgid(int(gid)).gr_name
        except (KeyError,ValueError,OverflowError):
            return gid
    
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
        if not self.exists:
            return FilesystemObjectType.MISSING
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

    @property
    def md5sum(self):
        chksum = hashlib.md5()
        with open(self.path,'rb') as f:
            for block in iter(lambda: f.read(MD5_BLOCK_SIZE),''):
                chksum.update(block)
        return chksum.hexdigest()

    @property
    def linux_permissions(self):
        st_mode = self._st.st_mode
        perms = "%s%s%s%s%s%s%s%s%s" % \
                (('r' if st_mode & stat.S_IRUSR else '-'),
                 ('w' if st_mode & stat.S_IWUSR else '-'),
                 ('x' if st_mode & stat.S_IXUSR else '-'),
                 ('r' if st_mode & stat.S_IRGRP else '-'),
                 ('w' if st_mode & stat.S_IWGRP else '-'),
                 ('x' if st_mode & stat.S_IXGRP else '-'),
                 ('r' if st_mode & stat.S_IROTH else '-'),
                 ('w' if st_mode & stat.S_IWOTH else '-'),
                 ('x' if st_mode & stat.S_IXOTH else '-'))
        return perms

    @property
    def extension(self):
        return '.'.join(os.path.basename(self.path).split('.')[1:])

    @property
    def type_extension(self):
        if self.iscompressed:
            try:
                return self.extension.split('.')[-2]
            except IndexError:
                return ""
        else:
            return self.extension.split('.')[-1]

    @property
    def iscompressed(self):
        return (self.path.split('.')[-1] in ('gz','bz2'))

class FilesystemObjectIndex(object):
    """
    Index of information about objects in a directory
    """
    def __init__(self,dirn):
        """
        """
        self._dirn = os.path.abspath(dirn)
        self._objects = {}
        self._names = []
        self._build()

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
    
    def _build(self):
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
    Compare two FilesystemObjectIndexes
    """
    # Define a named tuple to return the results with
    FilesystemObjectIndexComparison = collections.namedtuple(
    "FilesystemObjectIndexComparison",
    ['missing',
     'extra',
     'restricted_source',
     'restricted_target',
     'changed_type',
     'changed_size',
     'changed_md5',
     'changed_link',
     'changed_time',],)
    # Missing and modified objects
    missing = set()
    changed_type = set()
    changed_size = set()
    changed_md5 = set()
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
                    if src_obj.md5sum != tgt_obj.md5sum:
                        changed_md5.add(name)
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
    return FilesystemObjectIndexComparison(
        missing=sorted(list(missing)),
        extra=sorted(list(extra)),
        restricted_source=sorted(list(restricted_src)),
        restricted_target=sorted(list(restricted_tgt)),
        changed_type=sorted(list(changed_type)),
        changed_size=sorted(list(changed_size)),
        changed_md5=sorted(list(changed_md5)),
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

def find(indx,exts=None,users=None,nocompressed=False):
    """
    Find matching objects in an ObjectIndex
    """
    matches = list()
    if exts is None and users is None:
        return matches
    if exts is not None:
        exts = [x.strip('.') for x in exts.split(',')]
        for name in indx.names:
            obj = indx[name]
            for ext in exts:
                if ext == obj.type_extension:
                    matches.append(name)
                    break
    else:
        matches = indx.names
    if users is not None:
        users = [x for x in users.split(',')]
        matches = filter(lambda x: indx[x].username in users,
                         matches)
    if nocompressed:
        matches = filter(lambda x: not indx[x].iscompressed,
                         matches)
    return sorted(matches)
