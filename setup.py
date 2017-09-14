from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize(["inputhandler.pyx","circulation.pyx","model.pyx"]), requires=['numpy']
)