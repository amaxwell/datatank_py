#
# http://peterdowns.com/posts/first-time-with-pypi.html
#
from setuptools import setup, find_packages
setup(
    name = "datatank_py",
    version = "0.3",
    packages = find_packages(),
    
    install_requires = ['numpy>1.0'],
    zip_safe = False
    author = "Adam R. Maxwell",
    author_email = "amaxwell@mac.com",
    description = "Python modules for creating and modifying DataTank files",
    license = "BSD New",
    url = "http://github.com/amaxwell/datatank_py",
    doc_url = "http://amaxwell.github.io/datatank_py",
    download_url = "http://github.com/amaxwell/datatank_py/tarball/0.3",
)
