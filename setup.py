import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "nexdatas",
    version = "0.0.1",
    author = "Jan Kotanski, Eugen Wintersberger , Halil Pasic",
    author_email = "jankotan@gmail.com, eugen.wintersberger@gmail.com, halil.pasic@gmail.com",
    description = ("Nexus Data writer implemented as a Tango Server"),
    license = "GNU GENERAL PUBLIC LICENSE v3",
    keywords = "writer Tango server nexus data",
    url = "http://code.google.com/p/nexdatas/",
    packages=['ndts'],
    long_description= read('README'),
    install_requires = [
        'numpy>=1.5.0',
        'PyTango>=7.2.2',
        'libpninx-python>=0.1.2'
        ],

)
