stoker: exploration/curation of NGS data
========================================

Utility to help with managing copies of directories containing NGS data and
analyses, developed within the Bioinformatics Core Facility (BCF) at the
University of Manchester (UoM).

Overview
********

``stoker`` provides a single utility of the same name, which has a number of
subcommands:

 * ``compare``: compares one directory against another, looking for missing,
   and extra file system 'objects' (files, directories and symbolic links),
   and objects which differ.
 * ``check_access``: checks the accessibility of a directory for the current
   user and identifies objects which are not accessible due to file system
   permissions

Installation
************

It is recommended to use::

    pip install .

from within the top-level source directory to install the package.

To use the package without installing it first you will need to add the
directory to your ``PYTHONPATH`` environment.

To install directly from github using ``pip``::

    pip install git+https://github.com/pjbriggs/stoker.git

Documentation
*************

This ``README`` currently comprises the whole of the documentation.

Authors
*******

 * Peter Briggs (``@pjbriggs``)
