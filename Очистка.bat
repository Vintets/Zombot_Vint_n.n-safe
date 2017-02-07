@echo off
@color 9A

:: ----delete files----------
@echo.
@echo.
@echo ---Delete Files---
@echo.

del /F /S /Q f_unknownEvent.txt
del /F /S /Q error_log.txt

::del /F /S /Q statistics\*\logs\*.*
for /d %%a in ( "statistics\*" )  do ( 
    del /F /S /Q statistics\%%~nxa\logs\*.*
    rmdir /Q statistics\%%~nxa\logs
    del /F /Q statistics\%%~nxa\compositions.soc
    del /F /Q statistics\%%~nxa\compositions
    )

::@echo.
::@echo.
::@echo ---Delete Hidden Files---
::@echo.
rem del /F /S /Q /AH statistics\*\logs\*.*
rem del /F /S /Q /AH %tmp%\*.*


:: ----delete directories----
::@echo.
::@echo.
::@echo ---Delete Directories---
::@echo.
::dir statistics\*\logs\ /ad /s /b /on >statistics\*\logs\file.txt
::for /F "tokens=*" %%i in (statistics\*\logs\file.txt) do rmdir /S /q "%%i"


:: ----delete file file.txt----
::@echo.
::@echo.
::@echo ---Delete file file.txt---
::@echo.
::del /F /S /Q statistics\*\logs\file.txt


::del /F /S /Q counts\*.*
:: ----delete directories counts----
@echo.
@echo.
@echo ---Delete file copatel---
@echo.

for /d %%a in ( "statistics\*" )  do ( 
    del /F /S /Q statistics\%%~nxa\copatel\*.*
    ::rmdir /Q statistics\%%~nxa\copatel
    )
    
::dir counts\ /ad /s /b /on >counts\file.txt
::for /F "tokens=*" %%i in (counts\file.txt) do rmdir /S /q "%%i"


:: ----delete file file.txt----
::@echo.
::@echo.
::@echo ---Delete file file.txt---
::@echo.
::del /F /S /Q statistics\*\logs\file.txt

@echo.
@echo.
@echo.
@echo ---Все файлы удалены!---
@sleep 5
@exit
@pause

