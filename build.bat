@echo off

del /f /q dist\*

pyinstaller run.py --onefile