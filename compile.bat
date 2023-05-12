@ECHO OFF
setup.py build_ext --inplace
rm build/ -rf
rm cythonLib/*.c
rm cythonLib/__pycache__/ -rf