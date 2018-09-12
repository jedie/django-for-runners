@echo off

REM ~ Windows Batch file to boot Django-ForRunners
REM ~
REM ~ It's create a virtualenv under "C:\Program Files\Django-ForRunners"
REM ~
REM ~ Start Django-ForRunners by double-click on:
REM ~
REM ~ "C:\Program Files\Django-ForRunners\Scripts\for_runners.exe"


title %~0
cd /d "%~dp0"

for /f "delims=;" %%i in ('py -V') do set VERSION=%%i
for /f "delims=;" %%i in ('py -3 -V') do set VERSION3=%%i

cls
echo.

if "%VERSION%"=="" (
    echo Sorry, Python 'py' launcher seems not to exist:
    echo.
    echo on
    py -V
    @echo off
    echo.
    echo Please install Python!
    echo.
    pause
    exit
)
echo Python 'py' launcher exists, default version is: %VERSION%

if "%VERSION3%"=="" (
    echo.
    echo Python v3 not installed!
    echo Sorry, Django-ForRunners doesn't run with Python v2 :(
    echo.
    pause
    exit
) else (
    echo Python v3 is: %VERSION%
)

whoami /groups | find "S-1-16-12288" > nul
if errorlevel 1 (
    echo.
    echo Error: You must start this batchfile with admin rights!
    echo.
    pause
    exit /b
)

set BASE_PATH=%ProgramFiles%\Django-ForRunners
echo on
mkdir "%BASE_PATH%"
@echo off
call:test_exist "%BASE_PATH%" "venv not found here:"

echo on
py -3 -m venv "%BASE_PATH%"
@echo off

set SCRIPT_PATH=%BASE_PATH%\Scripts
call:test_exist "%SCRIPT_PATH%" "venv/Script path not found here:"

set ACTIVATE=%SCRIPT_PATH%\activate.bat
call:test_exist "%ACTIVATE%" "venv activate not found here:"

echo on
call "%ACTIVATE%"

set PYTHON_EXE=%SCRIPT_PATH%\python.exe
call:test_exist "%PYTHON_EXE%" "Python not found here:"
echo on
"%PYTHON_EXE%" -m pip install --upgrade pip
@echo off

set PIP_EXE=%SCRIPT_PATH%\pip.exe
call:test_exist "%PIP_EXE%" "pip not found here:"
echo on
"%PIP_EXE%" install -e git+https://github.com/jedie/django-for-runners.git@master#egg=django-for-runners
@echo off

set REQ_TXT=%BASE_PATH%/src/django-for-runners/requirements.txt
call:test_exist "%REQ_TXT%" "Requirements not found here:"
echo on
"%PIP_EXE%" install -r "%REQ_TXT%"
@echo off

set EXE=%SCRIPT_PATH%/for_runners.exe
call:test_exist "%EXE%" "for_runners.exe not found here:"
echo on
"%EXE%" --version

echo on
explorer.exe %BASE_PATH%
@echo off
pause
exit 0


:test_exist
    if NOT exist "%~1" (
        echo.
        echo ERROR: %~2
        echo.
        echo "%~1"
        echo.
        pause
        exit 1
    )
goto:eof
