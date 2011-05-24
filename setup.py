#!/usr/bin/env python

import os
from setuptools import setup, find_packages
from pkg_resources import resource_filename

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup (
    name = "omnigraffle-export",
    version = "1.0",
    packages = find_packages('src'),
    package_dir = {'':'src'},
    install_requires = ['appscript'],
    author = "Filip Krikava",
    author_email = "krikava@gmail.com",
    long_description = read("README.md"),
    license = "http://www.opensource.org/licenses/mit-license.php",
    keywords = "omnigraffle export",
    url = "https://github.com/fikovnik/omnigraffle-export",
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        'Operating System :: MacOS :: MacOS X',
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.6",
        "Topic :: Utilities"
    ],
    entry_points = {
        'console_scripts': [
            'omnigraffle-export = omnigraffleexport:main',
            'omnigraffle-export-rubber = omnigraffleexport.rubber:main',
        ],
    },
    package_data = {
        '': ['setup-rubber.sh'],
    },    
    test_suite = 'test',
    zip_safe = True
)

print """
******************
* RUBBER support *
******************
If you want to setup rubber support run the setup-rubber.sh from: %s
""" % resource_filename(__name__, 'setup-rubber.sh')