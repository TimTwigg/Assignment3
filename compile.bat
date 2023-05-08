@ECHO OFF
setup.py build_ext --inplace
rm build/ -rf
rm cythonLib/*.c
rm __pycache__/ -rf