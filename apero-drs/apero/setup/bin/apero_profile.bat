@echo off

:: Set the path to profiles.ini
set PROFILE_FILE=%USERPROFILE%\.apero\profiles.ini

:: Check if profiles.ini exists
if not exist "%PROFILE_FILE%" (
    echo Error: profiles.ini file not found.
    exit /b 1
)

:: Check if profile name is provided as an argument
if "%~1"=="" (
    echo Usage: %~nx0 profile_name
    exit /b 1
)

set PROFILE_NAME=%~1

:: Read profiles.ini and find the path for the provided profile
for /f "tokens=1,* delims==" %%a in (%PROFILE_FILE%) do (
    if /i "%%a"=="%PROFILE_NAME%" set PROFILE_PATH=%%b
)

:: Check if the profile path was found
if "%PROFILE_PATH%"=="" (
    echo Profile %PROFILE_NAME% not found in %PROFILE_FILE%.
    echo
    echo Available profiles are:
    for /f "tokens=1 delims==" %%a in (profiles.ini) do (
        echo %%a
    )
    echo Or run apero_setup.py to create a new profile.
    exit /b 1
)

:: Determine setup script based on OS
set SETUP_SCRIPT=%PROFILE_PATH%\setup.bat

:: Run the setup script if it exists
if exist "%SETUP_SCRIPT%" (
    call "%SETUP_SCRIPT%"
) else (
    echo Setup script not found: %SETUP_SCRIPT%
    exit /b 1
)
