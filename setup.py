#
# http://peterdowns.com/posts/first-time-with-pypi.html
#
from setuptools import setup, find_packages
setup(
    name = "datatank_py",
    version = "0.5",
    packages = find_packages(),
    
    install_requires = ['numpy>1.0'],
    zip_safe = False,
    author = "Adam R. Maxwell",
    author_email = "amaxwell@mac.com",
    description = """
        =============
        WHAT IS THIS?
        =============

        This is a Python module that allows you to read and write DataTank data files using
        Python. `DataTank <http://visualdatatools.com/DataTank/>`_ is a visualization and 
        analysis tool for Mac OS X, but datatank_py is cross-platform.
        
        `Documentation <http://amaxwell.github.io/datatank_py>`_

        Although DataTank itself is proprietary (now free of
        charge for students and postdocs), it includes open-source C++ libraries for most
        of the internal data structures, so you can easily create data files to be loaded
        into it. The datatank_py module is a reimplementation of the C++ libraries, so
        tends to be more Pythonic.""",
    license = "BSD New",
    url = "http://github.com/amaxwell/datatank_py",
    download_url = "http://github.com/amaxwell/datatank_py/tarball/0.4",
)
