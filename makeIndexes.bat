@ECHO OFF

main.py --index -d test -op -b none
RENAME index indexSmall
ECHO.

main.py --index -d large -op -b none
RENAME index indexLarge
ECHO.