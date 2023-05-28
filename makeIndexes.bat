@ECHO OFF

main.py --index -d test -op -b none
MOVE summary.txt index/summary.txt
RENAME index indexSmall
ECHO.

main.py --index -d large -op -b none
MOVE summary.txt index/summary.txt
RENAME index indexLarge
ECHO.