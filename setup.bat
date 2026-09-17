@echo off
echo ================================================
echo   Avatar Studio - Instalacao Local (Windows)
echo ================================================
echo.

:: Verificar Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERRO: Python nao encontrado!
    echo Instale o Python em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Criando ambiente virtual...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/3] Instalando dependencias...
pip install --quiet --upgrade pip
pip install --quiet streamlit requests

echo [3/3] Abrindo o Avatar Studio no navegador...
echo.
echo ================================================
echo   Avatar Studio iniciando em:
echo   http://localhost:8501
echo ================================================
echo.
echo Deixe esta janela aberta enquanto usar o Avatar Studio.
echo Para fechar, pressione Ctrl+C nesta janela.
echo.
streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
pause
