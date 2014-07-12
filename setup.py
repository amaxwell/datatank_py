#
# http://peterdowns.com/posts/first-time-with-pypi.html
#
from setuptools import setup, find_packages

# http://docs.python.org/2.7/distutils/packageindex.html#the-pypirc-file
with open("README.rst") as readme:
    long_description = readme.read()

setup(
    name = "datatank_py",
    version = "0.7",
    packages = find_packages(),
    
    install_requires = ['numpy>1.0'],
    zip_safe = False,
    author = "Adam R. Maxwell",
    author_email = "amaxwell@mac.com",
    description = "Module for reading and writing DataTank files",
    long_description = long_description,
    license = "BSD New",
    url = "http://github.com/amaxwell/datatank_py",
    download_url = "http://github.com/amaxwell/datatank_py/tarball/0.7",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft",
        "Operating System :: POSIX",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
