@echo off
echo Compilando EasyBooks...

REM Limpia las carpetas de compilación anteriores si existen
rmdir /S /Q "build"
rmdir /S /Q "dist"

REM Ejecuta PyInstaller para compilar el archivo .py a .exe
"pyinstaller" --onefile -w -i "icono.ico" "EasyBooks.py"

echo Compilación completa.
pause
