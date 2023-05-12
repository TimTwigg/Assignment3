@ECHO OFF
setup.py build_ext --inplace
rm build/ -rf
rm src/*.c
rm src/__pycache__/ -rf