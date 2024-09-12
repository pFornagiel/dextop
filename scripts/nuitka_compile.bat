@echo off

set CURRENT_DIR=%CD%

py -X utf8 -m nuitka ^
    --standalone ^
    --mingw64 ^
    --clang ^
    --enable-plugin=tk-inter ^
    --include-package-data=tksvg ^
    --windows-icon-from-ico=%CURRENT_DIR%\\assets\\dextop_icon.png ^
    --include-data-dir=assets=assets ^
    --windows-console-mode=disable ^
    Dextop.py

@REM Copy libtksvg.dll manually. Cannot get it working with Nuitka configuration.
xcopy %CURRENT_DIR%\.venv\Lib\site-packages\tksvg\libtksvg.dll Dextop.dist\tksvg\ /Y

pause
