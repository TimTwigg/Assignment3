@ECHO OFF

@REM main.py --index -d test -op -b none
@REM RENAME index indexSmall
@REM ECHO.

main.py --index -d large -op -b none
RENAME index indexLarge
ECHO.