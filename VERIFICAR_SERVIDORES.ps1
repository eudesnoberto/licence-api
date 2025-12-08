# Script para verificar status de todos os servidores
# Execute: .\VERIFICAR_SERVIDORES.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔍 Verificação de Servidores" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$servers = @(
    @{
        Name = "Servidor Principal"
        URL = "https://api.fartgreen.fun"
    },
    @{
        Name = "Render (Backup 1)"
        URL = "https://licence-api-zsbg.onrender.com"
    },
    @{
        Name = "Koyeb (Backup 2)"
        URL = "https://shiny-jemmie-easyplayrockola-6d2e5ef0.koyeb.app"
    }
)

$results = @()

foreach ($server in $servers) {
    Write-Host "Testando: $($server.Name)" -ForegroundColor Yellow
    Write-Host "  URL: $($server.URL)" -ForegroundColor Gray
    
    # Testar /health
    try {
        $healthResponse = Invoke-WebRequest -Uri "$($server.URL)/health" -Method GET -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        $healthStatus = $healthResponse.StatusCode
        $healthTime = $healthResponse.Headers.'X-Response-Time'
        
        if ($healthStatus -eq 200) {
            Write-Host "  ✅ /health: OK (Status: $healthStatus)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  /health: Status $healthStatus" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ /health: FALHOU - $($_.Exception.Message)" -ForegroundColor Red
        $healthStatus = "ERRO"
    }
    
    # Testar /ping
    try {
        $pingResponse = Invoke-WebRequest -Uri "$($server.URL)/ping" -Method GET -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        $pingStatus = $pingResponse.StatusCode
        
        if ($pingStatus -eq 200) {
            $pingData = $pingResponse.Content | ConvertFrom-Json
            Write-Host "  ✅ /ping: OK - $($pingData.message)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  /ping: Status $pingStatus" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ /ping: FALHOU - $($_.Exception.Message)" -ForegroundColor Red
        $pingStatus = "ERRO"
    }
    
    $results += @{
        Name = $server.Name
        URL = $server.URL
        Health = $healthStatus
        Ping = $pingStatus
    }
    
    Write-Host ""
}

# Resumo
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📊 RESUMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$online = 0
$offline = 0

foreach ($result in $results) {
    if ($result.Health -eq 200 -and $result.Ping -eq 200) {
        Write-Host "✅ $($result.Name): ONLINE" -ForegroundColor Green
        $online++
    } elseif ($result.Health -eq 200 -or $result.Ping -eq 200) {
        Write-Host "⚠️  $($result.Name): PARCIALMENTE ONLINE" -ForegroundColor Yellow
        $online++
    } else {
        Write-Host "❌ $($result.Name): OFFLINE" -ForegroundColor Red
        $offline++
    }
}

Write-Host ""
Write-Host "Total: $online online, $offline offline" -ForegroundColor Cyan
Write-Host ""

if ($offline -eq 0) {
    Write-Host "✅ Todos os servidores estão online!" -ForegroundColor Green
} elseif ($online -gt 0) {
    Write-Host "⚠️  Alguns servidores estão offline, mas há redundância disponível." -ForegroundColor Yellow
} else {
    Write-Host "❌ Todos os servidores estão offline!" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

