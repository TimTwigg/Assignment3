from setuptools import setup
from Cython.Build import cythonize

setup(
    name = "cythonLib",
    ext_modules = cythonize(["cythonLib/*.pyx"]),
    zip_safe = False
)