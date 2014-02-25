from setuptools import setup
setup(
    name = "datatank_py",
    version = "0.1",
    packages = [ "datatank_py" ],
    
    install_requires = ['numpy>1.0'],
    # package_data = {
    #     "" : [ "*.tank", "*.markdown", "*.txt" ]
    # },
    
    author = "Adam R. Maxwell",
    author_email = "amaxwell@mac.com",
    description = "Python modules for creating and modifying DataTank files",
    license = "BSD",
)
