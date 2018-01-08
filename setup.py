"""Description

Setup script to install arqivr package

Copyright (C) University of Manchester 2018 Peter Briggs

"""

# Setup for installation etc
from setuptools import setup
import arqivr
setup(
    name = "arqivr",
    version = arqivr.get_version(),
    description = 'Utility for curation of NGS data',
    long_description = """Utility to help examine and archive NGS data from
SOLiD and Illumina sequencing platforms""",
    url = 'https://github.com/pjbriggs/arqivr',
    maintainer = 'Peter Briggs',
    maintainer_email = 'peter.briggs@manchester.ac.uk',
    packages = ['arqivr'],
    entry_points = { 'console_scripts':
                     ['arqivr = arqivr.cli:main',]
                 },
    license = 'MIT',
    # Pull in dependencies
    ##install_requires = ['genomics-bcftbx',
    ##                    'auto_process_ngs'],
    # Enable 'python setup.py test'
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    zip_safe = False
)
