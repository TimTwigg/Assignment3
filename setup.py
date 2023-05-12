from setuptools import setup
from Cython.Build import cythonize

setup(
    name = "src",
    ext_modules = cythonize(["src/*.pyx"], compiler_directives = {"language_level": 3}),
    zip_safe = False
)