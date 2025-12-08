# ============================================================================
# Script para Subir Arquivos para GitHub
# ============================================================================
# Este script prepara e envia os arquivos para o repositório GitHub
# Repositório: https://github.com/eudesnoberto/licence-api.git
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SUBINDO ARQUIVOS PARA GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se Git está instalado
try {
    $gitVersion = git --version
    Write-Host "✓ Git encontrado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git não encontrado! Instale Git primeiro." -ForegroundColor Red
    Write-Host "  Download: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Navega para a pasta do projeto
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "Pasta atual: $PWD" -ForegroundColor Gray
Write-Host ""

# Verifica se já é um repositório Git
if (Test-Path ".git") {
    Write-Host "✓ Repositório Git já inicializado" -ForegroundColor Green
} else {
    Write-Host "Inicializando repositório Git..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Repositório inicializado" -ForegroundColor Green
}

# Verifica se remote origin já existe
$remoteExists = git remote | Select-String -Pattern "origin"
if ($remoteExists) {
    Write-Host "✓ Remote 'origin' já configurado" -ForegroundColor Green
    $currentRemote = git remote get-url origin
    Write-Host "  URL atual: $currentRemote" -ForegroundColor Gray
} else {
    Write-Host "Configurando remote 'origin'..." -ForegroundColor Yellow
    git remote add origin https://github.com/eudesnoberto/licence-api.git
    Write-Host "✓ Remote configurado" -ForegroundColor Green
}

Write-Host ""
Write-Host "Adicionando arquivos..." -ForegroundColor Yellow

# Adiciona todos os arquivos (exceto os ignorados pelo .gitignore)
git add .

Write-Host "✓ Arquivos adicionados" -ForegroundColor Green

Write-Host ""
Write-Host "Verificando status..." -ForegroundColor Yellow
$status = git status --short
if ($status) {
    Write-Host "Arquivos para commit:" -ForegroundColor Cyan
    Write-Host $status -ForegroundColor Gray
    Write-Host ""
    
    $commitMessage = "Initial commit - API de licenciamento com redundância"
    Write-Host "Fazendo commit: '$commitMessage'" -ForegroundColor Yellow
    git commit -m $commitMessage
    
    Write-Host "✓ Commit realizado" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Enviando para GitHub..." -ForegroundColor Yellow
    Write-Host "  (Pode pedir usuário/senha - use Personal Access Token)" -ForegroundColor Gray
    Write-Host ""
    
    # Tenta criar branch main se não existir
    git branch -M main 2>$null
    
    # Push para GitHub
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  ✓ ARQUIVOS ENVIADOS COM SUCESSO!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Repositório: https://github.com/eudesnoberto/licence-api" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Próximo passo: Fazer deploy no Render.com" -ForegroundColor Yellow
        Write-Host "  Guia: PASSO_A_PASSO_GITHUB_RENDER.md" -ForegroundColor Gray
    } else {
        Write-Host ""
        Write-Host "✗ Erro ao enviar para GitHub" -ForegroundColor Red
        Write-Host ""
        Write-Host "Possíveis causas:" -ForegroundColor Yellow
        Write-Host "  1. Repositório não existe ou você não tem permissão" -ForegroundColor Gray
        Write-Host "  2. Precisa usar Personal Access Token (não senha)" -ForegroundColor Gray
        Write-Host "  3. Repositório já tem conteúdo (use: git pull --allow-unrelated-histories)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Como criar Personal Access Token:" -ForegroundColor Cyan
        Write-Host "  GitHub → Settings → Developer settings → Personal access tokens" -ForegroundColor Gray
    }
} else {
    Write-Host "✓ Nenhuma mudança para commitar" -ForegroundColor Green
    Write-Host "  (Todos os arquivos já estão no GitHub)" -ForegroundColor Gray
}

Write-Host ""

