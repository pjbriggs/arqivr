#!/usr/bin/env python3
#
#     index.py: indexing classes and functions
#     Copyright (C) University of Manchester 2018-2021 Peter Briggs
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
COMPRESSED_FILE_EXTENSIONS = ('gz','bz2')

# File types
class FilesystemObjectType(object):
    FILE = 0
    DIRECTORY = 1
    SYMLINK = 2
    MISSING = 3
    UNKNOWN = 4

class FilesystemObjectStat(object):
    """
    Wrapper for result of os.lstat(...)

    Create a new instance for a file or other filesystem
    object, then use the 'get' method to fetch values for
    different attributes.

    The attribute names are the same as those provided by
    the result of os.lstat, with the leading 'st_' removed,
    e.g.

    st_mtime (in os.lstat) -> mtime

    Usage example:

    >>> st = FilesystemObjectStat("test.txt")
    >>> st.get("mtime")
    1525350206.9344375

    This is the equivalent of:

    >>> os.lstat("test.txt").st_mtime
    1525350206.9344375
    """
    def __init__(self,path):
        try:
            self._st = os.lstat(path)
        except OSError:
            self._st = None

    def get(self,attr):
        try:
            return getattr(self._st,"st_%s" % attr)
        except Exception as ex:
            if self._st is None:
                return None
            else:
                raise ex

class FilesystemObject(object):
    """
    Store information about file system object
    """
    def __init__(self,path):
        """
        """
        self.path = os.path.abspath(path)
        self.stat = FilesystemObjectStat(self.path)
        self._exists = None

    @property
    def exists(self):
        if self._exists is None:
            self._exists = os.path.lexists(self.path)
        return self._exists

    @property
    def timestamp(self):
        return self.stat.get("mtime")

    @property
    def size(self):
        return self.stat.get("size")

    @property
    def uid(self):
        return self.stat.get("uid")

    @property
    def username(self):
        uid = self.uid
        if uid is None:
            return None
        try:
            return pwd.getpwuid(int(uid)).pw_name
        except (KeyError,ValueError,OverflowError):
            return uid

    @property
    def gid(self):
        return self.stat.get("gid")

    @property
    def groupname(self):
        gid = self.gid
        if gid is None:
            return None
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
        if self.exists:
            return os.readlink(self.path)
        else:
            return None

    @property
    def ishidden(self):
        for ele in self.path.split(os.sep):
            if ele.startswith('.'):
                return True
        return False

    @property
    def isaccessible(self):
        if not self.exists:
            return False
        st_mode = self.stat.get("mode")
        if self.uid == os.getuid():
            return bool(st_mode & stat.S_IRUSR)
        if self.gid in os.getgroups():
            return bool(st_mode & stat.S_IRGRP)
        return bool(st_mode & stat.S_IROTH)

    @property
    def md5sum(self):
        if not self.exists:
            return None
        chksum = hashlib.md5()
        with open(self.path,"rb",buffering=MD5_BLOCK_SIZE) as fp:
            for block in iter(fp.read,''):
                if block:
                    chksum.update(block)
                else:
                    break
        return chksum.hexdigest()

    @property
    def linux_permissions(self):
        if not self.exists:
            return None
        st_mode = self.stat.get("mode")
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
        return (self.path.split('.')[-1] in COMPRESSED_FILE_EXTENSIONS)

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
        print("Indexing objects in %s" % self._dirn)
        for d in os.walk(self._dirn):
            for f in d[1]:
                self._add_object(d[0],f)
            for f in d[2]:
                self._add_object(d[0],f)
        print("Added %d objects" % len(self))

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
        try:
            if obj.isaccessible:
                continue
        except AttributeError:
            pass
        inaccessible.append(name)
    return inaccessible

def find(indx,exts=None,users=None,size=None,only_hidden=False,
         nosymlinks=False,nocompressed=False):
    """
    Find matching objects in an ObjectIndex
    """
    matches = list()
    if exts is None and \
       users is None and \
       size is None and \
       only_hidden is False:
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
    if size is not None:
        matches = filter(lambda x: indx[x].isfile and indx[x].size >= size,
                         matches)
    if only_hidden:
        matches = filter(lambda x: indx[x].ishidden,
                         matches)
    if nosymlinks:
        matches = filter(lambda x: not indx[x].islink,
                         matches)
    if nocompressed:
        matches = filter(lambda x: not indx[x].iscompressed,
                         matches)
    return sorted(matches)
