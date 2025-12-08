# Script PowerShell para Publicar no Cloudflare
# Execute este script para automatizar o processo de publicação

Write-Host "🚀 Publicando Sistema no Cloudflare..." -ForegroundColor Cyan
Write-Host ""

# Verificar se está na pasta correta
if (-not (Test-Path "frontend") -or -not (Test-Path "api")) {
    Write-Host "❌ Erro: Execute este script na pasta raiz do projeto (C:\protecao)" -ForegroundColor Red
    exit 1
}

# ============================================================================
# PARTE 1: Compilar Frontend
# ============================================================================
Write-Host "📦 Compilando Frontend..." -ForegroundColor Yellow

Set-Location frontend

# Verificar se node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "  Instalando dependências..." -ForegroundColor Gray
    npm install
}

# Criar .env.production se não existir
if (-not (Test-Path ".env.production")) {
    Write-Host "  Criando .env.production..." -ForegroundColor Gray
    @"
VITE_API_BASE_URL=https://api.fartgreen.fun
"@ | Out-File -Encoding utf8 .env.production
    Write-Host "  ✅ Arquivo .env.production criado" -ForegroundColor Green
}

# Compilar
Write-Host "  Compilando para produção..." -ForegroundColor Gray
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Erro ao compilar frontend!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "  ✅ Frontend compilado com sucesso!" -ForegroundColor Green
Write-Host ""

Set-Location ..

# ============================================================================
# PARTE 2: Verificar Backend
# ============================================================================
Write-Host "🔧 Verificando Backend..." -ForegroundColor Yellow

Set-Location api

# Verificar se .env existe
if (-not (Test-Path ".env")) {
    Write-Host "  ⚠️  Arquivo .env não encontrado!" -ForegroundColor Yellow
    Write-Host "  Criando .env com valores padrão..." -ForegroundColor Gray
    
    # Gerar credenciais aleatórias
    $apiKey = -join ((48..57) + (65..90) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    $sharedSecret = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    
    @"
API_KEY=$apiKey
SHARED_SECRET=$sharedSecret
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true
MAX_TIME_SKEW=14400
DB_PATH=./license.db
ADMIN_DEFAULT_USER=admin
ADMIN_DEFAULT_PASSWORD=admin123
SMTP_ENABLED=false
ENABLE_CLONE_DETECTION=true
MAX_SIMULTANEOUS_IPS=1
CLONE_DETECTION_WINDOW=300
OFFLINE_GRACE_PERIOD_DAYS=7
"@ | Out-File -Encoding utf8 .env
    
    Write-Host "  ✅ Arquivo .env criado" -ForegroundColor Green
    Write-Host "  📝 Anote suas credenciais:" -ForegroundColor Yellow
    Write-Host "     API_KEY: $apiKey" -ForegroundColor Gray
    Write-Host "     SHARED_SECRET: $sharedSecret" -ForegroundColor Gray
}

# Verificar se ambiente virtual existe
if (-not (Test-Path ".venv")) {
    Write-Host "  Criando ambiente virtual..." -ForegroundColor Gray
    python -m venv .venv
}

# Verificar se dependências estão instaladas
if (-not (Test-Path ".venv\Scripts\pip.exe")) {
    Write-Host "  ⚠️  Ambiente virtual não configurado corretamente" -ForegroundColor Yellow
}

Write-Host "  ✅ Backend verificado" -ForegroundColor Green
Write-Host ""

Set-Location ..

# ============================================================================
# PARTE 3: Instruções
# ============================================================================
Write-Host "📋 Próximos Passos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. PUBLICAR FRONTEND NO CLOUDFLARE PAGES:" -ForegroundColor Yellow
Write-Host "   a) Acesse: https://dash.cloudflare.com" -ForegroundColor Gray
Write-Host "   b) Vá em 'Pages' > 'Create a project'" -ForegroundColor Gray
Write-Host "   c) Faça upload da pasta: frontend\dist\" -ForegroundColor Gray
Write-Host "   d) Configure domínio: fartgreen.fun" -ForegroundColor Gray
Write-Host "   e) Adicione variável: VITE_API_BASE_URL = https://api.fartgreen.fun" -ForegroundColor Gray
Write-Host ""
Write-Host "2. CONFIGURAR CLOUDFLARE TUNNEL (Backend):" -ForegroundColor Yellow
Write-Host "   a) Instale: choco install cloudflared" -ForegroundColor Gray
Write-Host "   b) Login: cloudflared tunnel login" -ForegroundColor Gray
Write-Host "   c) Crie tunnel: cloudflared tunnel create api-backend" -ForegroundColor Gray
Write-Host "   d) Configure DNS: cloudflared tunnel route dns api-backend api.fartgreen.fun" -ForegroundColor Gray
Write-Host "   e) Inicie backend: cd api && .venv\Scripts\Activate.ps1 && python app.py" -ForegroundColor Gray
Write-Host "   f) Inicie tunnel: cloudflared tunnel run api-backend" -ForegroundColor Gray
Write-Host ""
Write-Host "3. TESTAR:" -ForegroundColor Yellow
Write-Host "   - Frontend: https://fartgreen.fun" -ForegroundColor Gray
Write-Host "   - API: https://api.fartgreen.fun/health" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 Para mais detalhes, consulte: GUIA_PUBLICACAO_CLOUDFLARE.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Preparação concluída!" -ForegroundColor Green

