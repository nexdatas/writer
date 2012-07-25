import os

__version__="0.0.1"

## reading a file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

## metadata for distutils
SETUPDATA=dict(
    name = "nexdatas",
    version = __version__,
    author = "Jan Kotanski, Eugen Wintersberger , Halil Pasic",
    author_email = "jankotan@gmail.com, eugen.wintersberger@gmail.com, halil.pasic@gmail.com",
    description = ("Nexus Data writer implemented as a Tango Server"),
    license = "GNU GENERAL PUBLIC LICENSE v3",
    keywords = "writer Tango server nexus data",
    url = "http://code.google.com/p/nexdatas/",
    packages=['ndts'],
#    package_data={'ndts': ['TDS']},
    long_description= read('README'),
)

## metadata for setuptools
SETUPTOOLSDATA= dict(
    include_package_data = True,
    install_requires = [
        'numpy>=1.5.0',
        'PyTango>=7.2.2',
        'libpninx-python>=0.1.2'
        ],
)

## the main function
def main():
    try:
        import setuptools
        SETUPDATA.update(SETUPTOOLSDATA)
        setuptools.setup(**SETUPDATA)
    except ImportError:
        import distutils.core
        distutils.core.setup(**SETUPDATA)
        

if __name__ == '__main__':
    main()

