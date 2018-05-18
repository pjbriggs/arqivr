#!/usr/bin/env python
#
#     cli.py: command line interfaces
#     Copyright (C) University of Manchester 2018 Peter Briggs
#
import argparse
import getpass
import commands
import index

def main(args=None):
    
    # Set up top-level command line parser
    parser = argparse.ArgumentParser(
        description="Examine and curate NGS data")

    # Add subcommand parsers
    subparsers = parser.add_subparsers(dest='command',
                                       help="Available commands")

    # 'compare' command
    cmp_parser = subparsers.add_parser("compare",
                                       help="compare two directories")
    cmp_parser.add_argument("source",default=None)
    cmp_parser.add_argument("target",default=None)

    # 'accessibility' command
    access_parser = subparsers.add_parser("check_access",
                                       help="check accessibility")
    access_parser.add_argument("dir",default=None)

    # 'find' command
    find_parser = subparsers.add_parser("find",
                                        help="search for files")
    find_parser.add_argument("dir",default=None,
                             help="directory to search")
    find_parser.add_argument("-e","--exts",dest='extensions',
                             default=None,
                             help="list of file extensions "
                             "separated by commas; only include "
                             "objects which have one of the "
                             "listed extensions")
    find_parser.add_argument("-s","--size",metavar='MINSIZE',
                             dest='min_size',default=None,
                             help="only include objects greater "
                             "than or equal to MINSIZE; MINSIZE "
                             "must be either: a number of bytes, "
                             "or an integer followed by 'K' (1024 "
                             "bytes), 'M' (1024K), or 'G' (1024M)")
    find_parser.add_argument("-u","--users",dest='users',
                             default=None,
                             help="list of one or more user names "
                             "separated by commas; only include "
                             "objects owned by one of the listed "
                             "users")
    find_parser.add_argument("-m","--mine",action='store_true',
                             help="only include objects which are "
                             "owned by the current user (overrides "
                             "--users)")
    find_parser.add_argument("--nocompressed",action='store_true',
                             help="don't include compressed objects "
                             "(i.e. those with %s extensions)" %
                             ', '.join(index.COMPRESSED_FILE_EXTENSIONS))
    find_parser.add_argument("-f","--full_paths",action='store_true',
                             help="report full paths to matching "
                             "objects")
    
    # Process the command line
    args = parser.parse_args()
    print "Command: %s" % args.command

    # Compare
    if args.command == "compare":
        commands.compare(args.source,args.target)

    # Accessibility
    if args.command == "check_access":
        commands.check_accessibility(args.dir)

    # Find
    if args.command == "find":
        if args.mine:
            users = getpass.getuser()
        else:
            users = args.users
        min_size = args.min_size
        if min_size:
            try:
                min_size = int(min_size)
            except ValueError:
                min_size,units = (int(min_size[:-1]),min_size[-1])
                if units == 'G':
                    min_size = min_size*1024*1024*1024
                elif units == 'M':
                    min_size = min_size*1024*1024
                elif units == 'K':
                    min_size = min_size*1024
                else:
                    raise Exception("%s: invalid size option" %
                                    args.min_size)
        commands.find(args.dir,
                      exts=args.extensions,
                      users=users,
                      size=min_size,
                      nocompressed=args.nocompressed,
                      full_paths=args.full_paths)


