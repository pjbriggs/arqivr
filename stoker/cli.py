#!/usr/bin/env python
#
#     cli.py: command line interfaces
#     Copyright (C) University of Manchester 2018 Peter Briggs
#
import argparse
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
    find_parser.add_argument("dir",default=None)
    find_parser.add_argument("-e","--exts",dest='extensions',
                             default=None)
    find_parser.add_argument("--nocompressed",action='store_true')
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
        commands.find(args.dir,
                      exts=args.extensions,
                      nocompressed=args.nocompressed,
                      full_paths=args.full_paths)


