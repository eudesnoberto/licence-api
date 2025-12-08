# Script de instalacao completa do sistema
# Uso: .\INSTALAR.ps1

Write-Host "Instalacao do Sistema de Licenciamento" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verifica Python
Write-Host "1. Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   [OK] $pythonVersion encontrado" -ForegroundColor Green
} catch {
    Write-Host "   [ERRO] Python nao encontrado!" -ForegroundColor Red
    Write-Host "   [INFO] Instale Python 3.11+ em: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "   [AVISO] Marque 'Add Python to PATH' durante a instalacao!" -ForegroundColor Yellow
    exit 1
}

# Verifica Node.js
Write-Host ""
Write-Host "2. Verificando Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "   [OK] $nodeVersion encontrado" -ForegroundColor Green
} catch {
    Write-Host "   [AVISO] Node.js nao encontrado (opcional para desenvolvimento)" -ForegroundColor Yellow
    Write-Host "   [INFO] Instale em: https://nodejs.org/ (se quiser rodar em modo dev)" -ForegroundColor Gray
}

# Instala dependencias do backend
Write-Host ""
Write-Host "3. Configurando Backend..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\api"

if (-not (Test-Path ".venv")) {
    Write-Host "   [INFO] Criando ambiente virtual..." -ForegroundColor Gray
    python -m venv .venv
}

Write-Host "   [INFO] Ativando ambiente virtual..." -ForegroundColor Gray
& .\.venv\Scripts\Activate.ps1

Write-Host "   [INFO] Instalando dependencias Python..." -ForegroundColor Gray
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Backend configurado!" -ForegroundColor Green
} else {
    Write-Host "   [ERRO] Erro ao instalar dependencias" -ForegroundColor Red
    exit 1
}

# Verifica arquivo .env do backend
if (-not (Test-Path ".env")) {
    Write-Host "   [INFO] Criando .env padrao..." -ForegroundColor Gray
    $envContent = @"
API_KEY=change_me_secret_key
SHARED_SECRET=change_me_shared_secret
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true
ALLOW_AUTO_PROVISION=false
ADMIN_DEFAULT_USER=admin
ADMIN_DEFAULT_PASSWORD=admin123
"@
    $envContent | Out-File -Encoding utf8 .env
    Write-Host "   [AVISO] Arquivo .env criado com valores padrao. Altere-os para producao!" -ForegroundColor Yellow
}

# Instala dependencias do frontend (se Node.js estiver disponivel)
Set-Location -Path "$PSScriptRoot\frontend"

if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Host ""
    Write-Host "4. Configurando Frontend..." -ForegroundColor Yellow
    
    if (-not (Test-Path "node_modules")) {
        Write-Host "   [INFO] Instalando dependencias Node.js..." -ForegroundColor Gray
        npm install --silent
    }
    
    if (-not (Test-Path ".env")) {
        Write-Host "   [INFO] Criando .env..." -ForegroundColor Gray
        "VITE_API_BASE_URL=http://127.0.0.1:5000" | Out-File -Encoding utf8 .env
    }
    
    Write-Host "   [OK] Frontend configurado!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "4. Frontend (pulando - Node.js nao encontrado)" -ForegroundColor Yellow
    Write-Host "   [INFO] Use a versao compilada em frontend/dist/ ou instale Node.js" -ForegroundColor Gray
}

Set-Location -Path $PSScriptRoot

# Resumo
Write-Host ""
Write-Host "[OK] Instalacao concluida!" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. Execute: .\iniciar-backend.ps1" -ForegroundColor White
Write-Host "  2. Execute: .\iniciar-frontend.ps1 (em outro terminal)" -ForegroundColor White
Write-Host "  3. Ou execute: .\iniciar-tudo.ps1 (inicia ambos)" -ForegroundColor White
Write-Host ""
Write-Host "Acesse: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Login: admin / admin123" -ForegroundColor Gray
Write-Host ""
