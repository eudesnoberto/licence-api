# Script para configurar MySQL remoto no servidor local
# Execute: .\CONFIGURAR_MYSQL_LOCAL.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔧 Configurar MySQL Remoto (Local)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$envFile = "api\.env"

# Verificar se .env existe
if (Test-Path $envFile) {
    Write-Host "✅ Arquivo .env encontrado" -ForegroundColor Green
    Write-Host ""
    Write-Host "Configuração atual:" -ForegroundColor Yellow
    Get-Content $envFile | Select-String -Pattern "DB_TYPE|MYSQL" | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Gray
    }
    Write-Host ""
    
    $dbType = (Get-Content $envFile | Select-String -Pattern "^DB_TYPE=").ToString().Split("=")[1].Trim()
    
    if ($dbType -eq "mysql") {
        Write-Host "✅ DB_TYPE já está configurado como 'mysql'" -ForegroundColor Green
    } else {
        Write-Host "⚠️  DB_TYPE está como '$dbType' (deve ser 'mysql')" -ForegroundColor Yellow
        Write-Host ""
        $alterar = Read-Host "Deseja alterar para 'mysql'? (S/N)"
        if ($alterar -eq "S" -or $alterar -eq "s") {
            (Get-Content $envFile) -replace "^DB_TYPE=.*", "DB_TYPE=mysql" | Set-Content $envFile
            Write-Host "✅ DB_TYPE alterado para 'mysql'" -ForegroundColor Green
        }
    }
} else {
    Write-Host "❌ Arquivo .env NÃO encontrado em api/.env" -ForegroundColor Red
    Write-Host ""
    Write-Host "Criando arquivo .env..." -ForegroundColor Yellow
    
    $criar = Read-Host "Deseja criar o arquivo .env com configuração MySQL? (S/N)"
    
    if ($criar -eq "S" -or $criar -eq "s") {
        Write-Host ""
        Write-Host "⚠️  IMPORTANTE: Você precisará preencher as credenciais MySQL" -ForegroundColor Yellow
        Write-Host ""
        
        $mysqlHost = Read-Host "MySQL Host (ex: 108.179.252.54)"
        $mysqlPort = Read-Host "MySQL Port (padrão: 3306)" 
        if ([string]::IsNullOrWhiteSpace($mysqlPort)) { $mysqlPort = "3306" }
        $mysqlDatabase = Read-Host "MySQL Database"
        $mysqlUser = Read-Host "MySQL User"
        $mysqlPassword = Read-Host "MySQL Password" -AsSecureString
        $mysqlPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPassword))
        
        $envContent = @"
# Configuração MySQL
DB_TYPE=mysql
MYSQL_HOST=$mysqlHost
MYSQL_PORT=$mysqlPort
MYSQL_DATABASE=$mysqlDatabase
MYSQL_USER=$mysqlUser
MYSQL_PASSWORD=$mysqlPasswordPlain

# API Keys (configure depois)
API_KEY=SUA_API_KEY_AQUI
SHARED_SECRET=SEU_SHARED_SECRET_AQUI
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true

# Admin padrão
ADMIN_DEFAULT_USER=admin
ADMIN_DEFAULT_PASSWORD=admin123
"@
        
        $envContent | Out-File -Encoding utf8 $envFile
        Write-Host ""
        Write-Host "✅ Arquivo .env criado em api/.env" -ForegroundColor Green
    } else {
        Write-Host "Operação cancelada." -ForegroundColor Yellow
        exit
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔍 Verificando pymysql..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se pymysql está instalado
try {
    $pymysqlCheck = python -c "import pymysql; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pymysql está instalado" -ForegroundColor Green
    } else {
        Write-Host "❌ pymysql NÃO está instalado" -ForegroundColor Red
        Write-Host ""
        $instalar = Read-Host "Deseja instalar pymysql agora? (S/N)"
        if ($instalar -eq "S" -or $instalar -eq "s") {
            Write-Host ""
            Write-Host "Instalando pymysql..." -ForegroundColor Yellow
            pip install pymysql
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ pymysql instalado com sucesso!" -ForegroundColor Green
            } else {
                Write-Host "❌ Erro ao instalar pymysql" -ForegroundColor Red
            }
        }
    }
} catch {
    Write-Host "⚠️  Não foi possível verificar pymysql" -ForegroundColor Yellow
    Write-Host "Tente instalar manualmente: pip install pymysql" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📋 Próximos Passos" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Reinicie o servidor:" -ForegroundColor White
Write-Host "   cd api" -ForegroundColor Gray
Write-Host "   python app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Verifique os logs - não deve aparecer:" -ForegroundColor White
Write-Host "   ⚠️  pymysql não instalado" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Teste a conexão:" -ForegroundColor White
Write-Host "   python testar_mysql.py" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

