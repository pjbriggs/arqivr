#!/usr/bin/env python
#
#     index.py: indexing classes and functions
#     Copyright (C) University of Manchester 2018 Peter Briggs
#

import os
import index

def _print_list(l):
    """
    """
    for i in l:
        print "\t%s" % i

def compare(source,target):
    """
    """
    source = index.FilesystemObjectIndex(source)
    target = index.FilesystemObjectIndex(target)
    diff = index.compare(source,target)
    print "%d missing objects" % len(diff.missing)
    _print_list(diff.missing)
    print "%d additional objects" % len(diff.extra)
    _print_list(diff.extra)
    print "%d objects changed type" % len(diff.changed_type)
    _print_list(diff.changed_type)
    print "%d objects changed size" % len(diff.changed_size)
    _print_list(diff.changed_size)
    print "%d objects changed MD5" % len(diff.changed_md5)
    _print_list(diff.changed_md5)
    print "%d objects changed time" % len(diff.changed_time)
    _print_list(diff.changed_time)
    print "%d objects changed link" % len(diff.changed_link)
    _print_list(diff.changed_link)
    print "%d restricted objects (source)" % len(diff.restricted_source)
    _print_list(diff.restricted_source)
    print "%d restricted objects (target)" % len(diff.restricted_target)
    _print_list(diff.restricted_target)

def check_accessibility(dirn):
    """
    """
    indx = index.FilesystemObjectIndex(dirn)
    inaccessible = index.check_accessibility(indx)
    print "%d inaccessible objects" % len(inaccessible)
    for name in inaccessible:
        obj = indx[name]
        print "\t%s %s:%s\t%s" % (obj.linux_permissions,
                                  obj.username,
                                  obj.groupname,
                                  name)

def find(dirn,exts=None,users=None,nocompressed=False,
         full_paths=False):
    """
    """
    indx = index.FilesystemObjectIndex(dirn)
    matches = index.find(indx,exts=exts,users=users,
                         nocompressed=nocompressed)
    print "%d matching objects" % len(matches)
    for name in matches:
        obj = indx[name]
        if full_paths:
            path = os.path.abspath(os.path.join(dirn,name))
        else:
            path = name
        print "%s%s" % (path,
                        (" -> %s" % obj.raw_symlink_target)
                        if obj.islink else "")
