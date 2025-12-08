# Script para iniciar o frontend (modo desenvolvimento)
# Uso: .\iniciar-frontend.ps1

Write-Host "Iniciando Frontend (Dashboard React)..." -ForegroundColor Cyan

# Verifica se Node.js esta instalado
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Node.js nao encontrado! Instale Node.js 18+ e adicione ao PATH." -ForegroundColor Red
    Write-Host "       Download: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Entra na pasta do frontend
Set-Location -Path "$PSScriptRoot\frontend"

# Verifica se node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "[INFO] Instalando dependencias do frontend..." -ForegroundColor Yellow
    npm install
}

# Verifica se o arquivo .env existe
if (-not (Test-Path ".env")) {
    Write-Host "[INFO] Criando arquivo .env..." -ForegroundColor Yellow
    "VITE_API_BASE_URL=http://127.0.0.1:5000" | Out-File -Encoding utf8 .env
    Write-Host "[OK] Arquivo .env criado com sucesso!" -ForegroundColor Green
}

# Inicia o servidor de desenvolvimento
Write-Host ""
Write-Host "[OK] Iniciando servidor Vite em http://localhost:5173" -ForegroundColor Green
Write-Host "     Pressione Ctrl+C para parar" -ForegroundColor Gray
Write-Host ""

npm run dev

