# Script para iniciar backend e frontend simultaneamente
# Uso: .\iniciar-tudo.ps1

Write-Host "Iniciando Sistema Completo..." -ForegroundColor Cyan
Write-Host ""

# Inicia o backend em uma nova janela
Write-Host "[INFO] Iniciando Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\iniciar-backend.ps1"

# Aguarda um pouco para o backend iniciar
Start-Sleep -Seconds 3

# Inicia o frontend em outra nova janela
Write-Host "[INFO] Iniciando Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\iniciar-frontend.ps1"

Write-Host ""
Write-Host "[OK] Sistema iniciado!" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "Dashboard: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login padrao:" -ForegroundColor Yellow
Write-Host "  Usuario: admin" -ForegroundColor Gray
Write-Host "  Senha:   admin123" -ForegroundColor Gray
Write-Host ""
Write-Host "[AVISO] Duas janelas foram abertas. Feche-as para parar os servidores." -ForegroundColor Yellow

