@echo off
REM Initialisiere Git und pushe das Projekt auf GitHub

REM Git-Repository initialisieren
git init

REM README erstellen, falls nicht vorhanden
if not exist README.md (
    echo "# ai.traiding" > README.md
)

REM Alle relevanten Dateien zum Commit hinzufügen
git add .

REM Initialen Commit durchführen
git commit -m "Initial commit"

REM Hauptbranch setzen
git branch -M main

REM Remote Repo hinzufügen (URL ggf. anpassen)
git remote add origin https://github.com/CallMeMell/ai.traiding.git

REM Push zum Remote Repo
git push -u origin main
pause
