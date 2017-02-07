@echo off
@color 9A

:: ----delete files----------
@echo.
@echo.
@echo ---Delete Files---
@echo.

del /F /Q f_unknownEvent.txt
del /F /Q error_log.txt

for /d %%a in ( "statistics\*" )  do ( 
    del /F /S /Q statistics\%%~nxa\logs\*.*
    rmdir /Q statistics\%%~nxa\logs
    del /F /Q statistics\%%~nxa\compositions.soc
    del /F /Q statistics\%%~nxa\compositions
    )
del /F /S /Q *.pyc


@echo.
@echo.
@echo.
@echo ---Все файлы удалены!---
@sleep 3
@exit
@pause

