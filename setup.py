from setuptools import setup
from Cython.Build import cythonize

setup(
    name = "cythonLib",
    ext_modules = cythonize(["cythonLib/*.pyx"], compiler_directives = {"language_level": 3}),
    zip_safe = False
)