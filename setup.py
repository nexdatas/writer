#!/usr/bin/env python3
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
## \file setup.py
# nxswriter installer

""" setup.py for Nexus Data Writer """


import os
from distutils.core import setup, Command

## package name
NDTS = "nxswriter"
## nxswriter imported package
INDTS = __import__(NDTS)


#__requires__ = 'nextdata ==%s' % INDTS.__version__

## reading a file
def read(fname):
    """ reading a file"""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


## test command class
class TestCommand(Command):

    ## user options
    user_options = []

    ## initializes options
    def initialize_options(self):
        pass

    ## finalizes options
    def finalize_options(self):
        pass

    ## runs command
    def run(self):
        import sys
        import subprocess
        errno = subprocess.call([sys.executable, 'test/runtest.py'])
        raise SystemExit(errno)


## required files
REQUIRED = [
    'numpy (>=1.5.0)',
    'PyTango (>=7.2.2)',
    'pni (>=1.0.0)'
]

## metadata for distutils
SETUPDATA = dict(
    name="nexdatas",
    version=INDTS.__version__,
    author="Jan Kotanski, Eugen Wintersberger , Halil Pasic",
    author_email="jankotan@gmail.com, eugen.wintersberger@gmail.com, "
    + "halil.pasic@gmail.com",
    description=("Nexus Data writer implemented as a Tango Server"),
    license="GNU GENERAL PUBLIC LICENSE v3",
    keywords="writer Tango server nexus data",
    url="https://github.com/jkotan/nexdatas/",
    packages=['nxswriter'],
    requires=REQUIRED,
    scripts=['NXSDataWriter'],
    cmdclass={'test': TestCommand},
    long_description=read('README')
)


## the main function
def main():
    """ the main function """
    setup(**SETUPDATA)


if __name__ == '__main__':
    main()
