@echo off
REM Script per inizializzare Git e sincronizzare con GitHub
REM Repository: IstatDataAna

echo ==========================================
echo Setup Git e Sync con GitHub
echo ==========================================
echo.

REM Verifica Git installato
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git non installato!
    echo Installa Git da: https://git-scm.com/downloads
    pause
    exit /b 1
)

echo [OK] Git trovato
echo.

REM Inizializza repository
echo [1] Inizializzazione repository Git locale...
git init

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Errore nell'inizializzazione
    pause
    exit /b 1
)

echo [OK] Repository inizializzato
echo.

REM Configura user
echo [2] Configurazione Git user...
set /p git_name="Inserisci il tuo nome per Git (es: Franco Rossi): "
set /p git_email="Inserisci la tua email GitHub: "

git config user.name "%git_name%"
git config user.email "%git_email%"

echo [OK] Configurazione completata
echo.

REM Aggiungi file
echo [3] Aggiunta file al repository...
git add .

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Errore nell'aggiunta file
    pause
    exit /b 1
)

echo [OK] File aggiunti
echo.

REM Commit
echo [4] Creazione primo commit...
git commit -m "Initial commit: ISTAT SDMX Python client with examples and documentation"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Errore nel commit
    pause
    exit /b 1
)

echo [OK] Commit creato
echo.

REM Istruzioni GitHub
echo ==========================================
echo PROSSIMI PASSI:
echo ==========================================
echo.
echo 1. Vai su GitHub: https://github.com/new
echo 2. Crea repository chiamato: IstatDataAna
echo 3. Lascia VUOTO (non inizializzare con README)
echo 4. Clicca 'Create repository'
echo.
set /p github_username="5. Username GitHub: "
echo.

REM Aggiungi remote
echo [5] Configurazione remote GitHub...
git remote add origin https://github.com/%github_username%/IstatDataAna.git

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Errore nell'aggiunta remote
    pause
    exit /b 1
)

echo [OK] Remote aggiunto
echo.

REM Rinomina branch
echo [6] Rinomina branch a 'main'...
git branch -M main
echo [OK] Branch rinominato
echo.

REM Push
echo [7] Push su GitHub...
echo.
echo ATTENZIONE: Usa un Personal Access Token!
echo.
echo Come creare token:
echo 1. Vai su: https://github.com/settings/tokens
echo 2. Generate new token (classic)
echo 3. Scope: 'repo'
echo 4. Usa il token come password
echo.
pause

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo SUCCESSO!
    echo ==========================================
    echo.
    echo Repository su: https://github.com/%github_username%/IstatDataAna
) else (
    echo.
    echo [ERROR] Errore nel push
    echo.
    echo Riprova con: git push -u origin main
)

echo.
pause
