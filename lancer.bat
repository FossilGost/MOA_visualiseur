@echo off
setlocal

cd /d "%~dp0"

set "VENV_DIR=MOAvenv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

echo.
echo === Visualisateur MOA ===

if not exist "%PYTHON_EXE%" (
    echo Creation de l'environnement virtuel...
    py -3 -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Impossible de creer le venv avec py -3. Nouvel essai avec python...
        python -m venv "%VENV_DIR%"
        if errorlevel 1 (
            echo Erreur: Python est introuvable ou le venv n'a pas pu etre cree.
            pause
            exit /b 1
        )
    )
)

echo Mise a jour de pip...
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 (
    echo Erreur pendant la mise a jour de pip.
    pause
    exit /b 1
)

if exist "requirements.txt" (
    echo Installation des dependances...
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Erreur pendant l'installation des dependances.
        pause
        exit /b 1
    )
)

echo Lancement de l'application...
"%PYTHON_EXE%" main.py

if errorlevel 1 (
    echo.
    echo L'application s'est arretee avec une erreur.
    pause
    exit /b 1
)

endlocal
