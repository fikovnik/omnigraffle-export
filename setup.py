import os
from setuptools import setup, find_packages

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
    classifiers=[
        "Development Status :: 4 - Beta",
        'Operating System :: MacOS :: MacOS X',
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points = {
        'console_scripts': [
            'omnigraffle-export = omnigraffleexport:main',
            'omnigraffle-export-rubber = omnigraffleexport.rubber:main',
        ],
    },    
    test_suite = 'test',
    zip_safe = True
)

