# Script para iniciar o backend Flask
# Uso: .\iniciar-backend.ps1

Write-Host "Iniciando Backend (API Flask)..." -ForegroundColor Cyan

# Verifica se Python esta instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Python nao encontrado! Instale Python 3.11+ e adicione ao PATH." -ForegroundColor Red
    exit 1
}

# Entra na pasta da API
Set-Location -Path "$PSScriptRoot\api"

# Verifica se o ambiente virtual existe
if (-not (Test-Path ".venv")) {
    Write-Host "[INFO] Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv .venv
}

# Ativa o ambiente virtual
Write-Host "[INFO] Ativando ambiente virtual..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Verifica se as dependencias estao instaladas
if (-not (Test-Path ".venv\Scripts\flask.exe")) {
    Write-Host "[INFO] Instalando dependencias..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Verifica se o arquivo .env existe
if (-not (Test-Path ".env")) {
    Write-Host "[AVISO] Arquivo .env nao encontrado. Usando configuracoes padrao." -ForegroundColor Yellow
    Write-Host "       Para personalizar, crie um arquivo .env na pasta api/" -ForegroundColor Gray
}

# Inicia o servidor
Write-Host ""
Write-Host "[OK] Iniciando servidor Flask em http://localhost:5000" -ForegroundColor Green
Write-Host "     Pressione Ctrl+C para parar" -ForegroundColor Gray
Write-Host ""

python app.py

