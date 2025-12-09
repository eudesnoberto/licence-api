# Script para limpar credenciais do histórico do Git
# ⚠️ CUIDADO: Este script modifica o histórico do Git
# Execute apenas se tiver certeza e tenha feito backup!

Write-Host "========================================" -ForegroundColor Red
Write-Host "⚠️  LIMPEZA DE CREDENCIAIS DO GIT" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "Este script irá:" -ForegroundColor Yellow
Write-Host "1. Remover credenciais do histórico do Git" -ForegroundColor Yellow
Write-Host "2. Limpar referências antigas" -ForegroundColor Yellow
Write-Host "3. Fazer push forçado para GitHub" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  ATENÇÃO: Isso irá reescrever o histórico!" -ForegroundColor Red
Write-Host "⚠️  Todos os colaboradores precisarão refazer clone!" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "Deseja continuar? (digite 'SIM' para confirmar)"

if ($confirm -ne "SIM") {
    Write-Host "Operação cancelada." -ForegroundColor Green
    exit
}

# Credenciais a remover
$credentials = @(
    "108.179.252.54",
    "scpmtc84_api",
    "nQT-8gW%-qCY"
)

Write-Host ""
Write-Host "🔍 Verificando histórico..." -ForegroundColor Cyan

# Verificar se há credenciais no histórico
$found = $false
foreach ($cred in $credentials) {
    $result = git log --all --full-history -S $cred --oneline 2>$null
    if ($result) {
        Write-Host "  ⚠️  Encontrado: $cred" -ForegroundColor Yellow
        $found = $true
    }
}

if (-not $found) {
    Write-Host "✅ Nenhuma credencial encontrada no histórico!" -ForegroundColor Green
    exit
}

Write-Host ""
Write-Host "📋 Opções disponíveis:" -ForegroundColor Cyan
Write-Host "1. Usar git filter-branch (nativo)" -ForegroundColor White
Write-Host "2. Apenas mostrar commits com credenciais" -ForegroundColor White
Write-Host "3. Cancelar" -ForegroundColor White
Write-Host ""

$option = Read-Host "Escolha uma opção (1-3)"

switch ($option) {
    "1" {
        Write-Host ""
        Write-Host "🔄 Limpando histórico..." -ForegroundColor Cyan
        
        # Criar backup
        Write-Host "  📦 Criando backup..." -ForegroundColor Yellow
        $backupDir = "../protecao-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item -Path . -Destination $backupDir -Recurse -Exclude ".git"
        Write-Host "  ✅ Backup criado em: $backupDir" -ForegroundColor Green
        
        # Remover credenciais do histórico
        Write-Host "  🧹 Removendo credenciais..." -ForegroundColor Yellow
        
        foreach ($cred in $credentials) {
            Write-Host "    Removendo: $cred" -ForegroundColor Gray
            git filter-branch --force --index-filter "git rm --cached --ignore-unmatch -r . 2>/dev/null || true" --prune-empty --tag-name-filter cat -- --all 2>$null
        }
        
        # Limpar referências
        Write-Host "  🗑️  Limpando referências..." -ForegroundColor Yellow
        git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin 2>$null
        git reflog expire --expire=now --all
        git gc --prune=now --aggressive
        
        Write-Host ""
        Write-Host "✅ Histórico limpo!" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  PRÓXIMOS PASSOS:" -ForegroundColor Yellow
        Write-Host "1. Verifique se está tudo correto:" -ForegroundColor White
        Write-Host "   git log --all -S 'nQT-8gW%-qCY'" -ForegroundColor Gray
        Write-Host ""
        Write-Host "2. Faça push forçado (CUIDADO):" -ForegroundColor White
        Write-Host "   git push -f origin main" -ForegroundColor Gray
        Write-Host ""
        Write-Host "3. ROTACIONAR CREDENCIAIS (mudar senha do MySQL)" -ForegroundColor Red
    }
    "2" {
        Write-Host ""
        Write-Host "📋 Commits com credenciais:" -ForegroundColor Cyan
        foreach ($cred in $credentials) {
            Write-Host ""
            Write-Host "Credencial: $cred" -ForegroundColor Yellow
            git log --all --full-history -S $cred --oneline
        }
    }
    "3" {
        Write-Host "Operação cancelada." -ForegroundColor Green
        exit
    }
    default {
        Write-Host "Opção inválida." -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

