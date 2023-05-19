@ECHO OFF

main.py --index -d test -op
ECHO.
main.py --refactor -i index -b long -p
MOVE summary.txt index/summary.txt
RENAME index indexSmall
ECHO.

main.py --index -d large -op
ECHO.
main.py --refactor -i index -b long -p
MOVE summary.txt index/summary.txt
RENAME index indexLarge
ECHO.